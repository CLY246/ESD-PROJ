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
        <tr v-for="item in savedCart" :key="item.ItemID">
          <td>1 x {{ item.ItemName }}</td>
          <td>${{ item.Price }}</td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td><strong>TOTAL</strong></td>
          <td>
            <strong>${{ transactiondata.Amount }}</strong>
          </td>
        </tr>
      </tfoot>
    </table>
    <RouterLink :to="'/'" class="backbtn">Return to Main Page</RouterLink>
  </div>
</template>

<script>
export default {
  data() {
    return {
      transactiondata: null,
      savedCart: [],
      storedUser: "",
    };
  },
  async mounted() {
    this.storedUser = localStorage.getItem("user_id");
    const transaction = sessionStorage.getItem("transaction");
    this.transactiondata = JSON.parse(transaction);
    const vendorCuisine = sessionStorage.getItem("cuisine");
    const vendorName = sessionStorage.getItem("vendorname");
    this.savedCart = JSON.parse(sessionStorage.getItem("cart") || "[]");
    sessionStorage.clear();

    const mappedCart = savedCart.map((item) => {
      return {
        Id: item.ItemID,
        VendorID: item.VendorID,
        VendorName: vendorName,
        Cuisine: vendorCuisine,
        ImageURL: item.ImageURL,
        OrderId: transactiondata.OrderID,
      };
    });

    this.requestBody = {
      UserOrdersAPI: {
        UserID: storedUser,
        OrderID: transactiondata.OrderID,
        OrderDetails: mappedCart,
      },
    };
    this.orderRequestBody = {
      UserID: storedUser,
      TotalAmount: transactiondata.Amount,
      TransactionID: transactiondata.TransactionID,
    };

    const cartitems = savedCart.map((item) => {
      return {
        ItemID: item.ItemID,
        ItemName: item.ItemName,
        Quantity: 1,
        Price: item.Price,
        VendorID: item.VendorID,
      };
    });

    this.orderData = {
      OrderID: transactiondata.OrderID,
      UserID: storedUser,
      TotalAmount: transactiondata.Amount,
      TransactionID: transactiondata.TransactionID,
      VendorID: savedCart.length > 0 ? savedCart[0].VendorID : null,
      VendorName: vendorName,
      Cuisine: vendorCuisine,
      ImageURL: savedCart.length > 0 ? savedCart[0].ImageURL : "",
      Items: cartitems,
    };
    console.log(this.orderData);

    this.postOrderHistory();
    this.postOrder();
  },
  methods: {
    async postOrderHistory() {
      try {
        const response = await fetch(
          "https://personal-aefq3pkb.outsystemscloud.com/OrderManagement/rest/OrderHistory/createHistory",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(this.requestBody),
          }
        );

        if (!response.ok) {
          throw new Error(
            `Server error: ${response.status} ${response.statusText}`
          );
        }

        const data = await response.json();
        console.log("Order history created successfully:", data);
      } catch (error) {
        console.error("Error posting order history:", error);
      }
    },
    async postOrder() {
      try {
        const response = await fetch("http://localhost:5003/orders", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(this.orderData),
        });
        if (!response.ok) {
          throw new Error(
            `Server error: ${response.status} ${response.statusText}`
          );
        }
        const data = await response.json();
        console.log("Order created successfully:", data);
      } catch (error) {
        console.error("Error creating order:", error);
      }
    },
  },
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
