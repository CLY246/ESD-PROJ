<template>
  <div class="success-container">
    <img
      class="successpng"
      src="https://cdn.dribbble.com/userupload/23589345/file/original-3facc6dbca53f39fa3175635da27a61a.gif"
    />
    <h1 class="success-message">Payment Successful!</h1>
    <p class="confirmation-text">
      The order confirmation has been sent to your email.
    </p>

    <table class="order-table">
      <thead>
        <tr>
          <th>Order Item</th>
          <th>Price</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in orderData?.Items || []" :key="item.ItemID">
          <td>{{ item.Quantity }} x {{ item.ItemName }}</td>
          <td>${{ (item.Price * item.Quantity).toFixed(2) }}</td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td><strong>TOTAL</strong></td>
          <td>
            <strong v-if="transactiondata">${{ transactiondata.Amount }}</strong>
            <strong v-else>$0.00</strong>
          </td>
        </tr>
      </tfoot>
    </table>
    <div v-if="isGroupOrder" class="split-payment-option">
    <p>This was a group order. Want to see how the bill is split?</p>
    <RouterLink :to="'/splitpayments'" class="splitbtn">
      View Split Payment
    </RouterLink>
    </div>
    <RouterLink :to="'/'" class="backbtn">Return to Main Page</RouterLink>
  </div>
</template>


<script>
export default {
  data() {
    return {
      transactiondata: {},
      orderData: {},
      requestBody: {},
    };
  },

  async mounted() {
    try {
      const transaction = JSON.parse(sessionStorage.getItem("transaction") || '{}');
      const cart = JSON.parse(sessionStorage.getItem("cart") || '[]');
      const userID = localStorage.getItem("user_id") || "";
      const vendorName = sessionStorage.getItem("vendorname") || "Vendor";
      const cuisine = sessionStorage.getItem("cuisine") || "Unknown";

      console.log("Success.vue mounted - Retrieved data:", {
        transaction,
        cartLength: cart.length,
        userID,
        vendorName,
        cuisine
      });

      // Check for missing data but don't throw an error - handle gracefully
      if (!transaction.OrderID || !transaction.TransactionID || !cart.length || !userID) {
        console.error("❌ Missing required data:", {
          hasOrderID: !!transaction.OrderID,
          hasTransactionID: !!transaction.TransactionID,
          cartLength: cart.length,
          hasUserID: !!userID
        });
        
        // Show message to user and redirect after a delay
        this.errorMessage = "Order information is incomplete. Redirecting to home page...";
        setTimeout(() => {
          this.$router.push('/');
        }, 3000);
        return; // Stop execution
      }

      this.transactiondata = transaction;

      // Format for Order History
      const mappedCart = cart.map(item => ({
        Id: item.ItemID,
        VendorID: item.VendorID,
        VendorName: vendorName,
        Cuisine: cuisine,
        ImageURL: item.ImageURL,
        OrderId: transaction.OrderID
      }));

      this.requestBody = {
        UserOrdersAPI: {
          UserID: userID,
          OrderID: transaction.OrderID,
          OrderDetails: mappedCart
        }
      };

      // Format for Order Management
      const cartItems = cart.map(item => ({
        ItemID: parseInt(item.ItemID),
        ItemName: item.ItemName,
        Quantity: parseInt(item.quantity) || 1,
        Price: parseFloat(item.Price) || 0,
        VendorID: parseInt(item.VendorID)
      }));

      this.orderData = {
        OrderID: transaction.OrderID,
        UserID: userID,
        TotalAmount: parseFloat(transaction.Amount),
        TransactionID: transaction.TransactionID,
        VendorID: parseInt(cart[0].VendorID),
        VendorName: vendorName,
        Cuisine: cuisine,
        ImageURL: cart[0]?.ImageURL || "",
        Items: cartItems
      };

      // ✅ Sequential flow
      await this.postOrderHistory();
      const orderResult = await this.postOrder();
      if (orderResult) await this.triggerAMQP(orderResult);

      setTimeout(() => {
        console.log("Clearing session storage after successful processing");
        sessionStorage.clear();
      }, 5000);
    
    } catch (error) {
      console.error("❌ Error in Success.vue mounted():", error);
      alert("Error: " + error.message);
    }
  },

  methods: {
    async postOrderHistory() {
      try {
        const res = await fetch("https://personal-aefq3pkb.outsystemscloud.com/OrderManagement/rest/OrderHistory/createHistory", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.requestBody)
        });

        if (!res.ok) throw new Error(`Order history failed: ${res.status}`);
        console.log("📦 Order history logged successfully");
      } catch (err) {
        console.error("❌ Order history logging error:", err);
      }
    },

    async postOrder() {
      try {
        const vendorRes = await fetch(`http://localhost:8000/vendors/${this.orderData.VendorID}`);
        const vendorInfo = await vendorRes.json();

        const res = await fetch("http://localhost:8000/trigger_ordermanagement", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            order: {
              UserID: this.orderData.UserID,
              VendorID: this.orderData.VendorID,
              TotalAmount: this.orderData.TotalAmount,
              OrderItems: this.orderData.Items
            },
            transaction_data: {
              OrderID: this.orderData.OrderID,
              TransactionID: this.orderData.TransactionID,
              Amount: this.orderData.TotalAmount
            },
            vendor_info: vendorInfo
          })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(JSON.stringify(data));
        console.log("✅ Order saved via trigger_ordermanagement:", data);

        return data; // return for AMQP use
      } catch (err) {
        console.error("❌ Order saving error:", err);
        return null;
      }
    },

    async triggerAMQP(orderMgmtData) {
      try {
        const newOrderID = orderMgmtData?.data?.data?.Order?.OrderID || this.orderData.OrderID;

        const res = await fetch("http://localhost:8000/trigger_amqp", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            order_result: orderMgmtData,
            order: {
              UserID: this.orderData.UserID,
              VendorID: this.orderData.VendorID,
              TotalAmount: this.orderData.TotalAmount,
              OrderItems: this.orderData.Items
            },
            new_order_id: newOrderID
          })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(JSON.stringify(data));
        console.log("📣 AMQP notification sent:", data);
      } catch (err) {
        console.error("❌ AMQP trigger error:", err);
      }
    }
  }
};
</script>



<style scoped>
.success-container {
  text-align: center;
  padding: 20px;
}
.success-message {
  color: green;
}
.successpng {
  height: 310px;
  width: 400px;
}
h1 {
  font-size: 30px;
}
p {
  font-size: 12px;
  color: gray;
}

.order-table {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  border-collapse: collapse;
  margin-top:30px
}
.order-table th {
  background-color: GhostWhite;
  color: black;
  text-align: left;
  padding: 10px;
}
.order-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
  font-size:12px;
}
tfoot td {
  font-weight: bold;
  border-bottom: 2px solid black;
}
.backbtn{
    border: 0px;
    padding: 15px 115px;
    border-radius: 25px;
    background-color: #b0c4de;
    display: inline-block;
    color: #fff;
    margin-top: 50px;
    text-decoration: none;
}
</style>
