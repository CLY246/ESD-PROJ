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

    <!-- <table class="order-table">
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
            <strong v-if="transactiondata"
              >${{ transactiondata.Amount }}</strong
            >
            <strong v-else>$0.00</strong>
          </td>
        </tr>
      </tfoot>
    </table> -->
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
import { useRoute } from 'vue-router'
import axios from 'axios'
export default {
  data() {
    return {
      loading: true,
      success: false,
      message: "",
    };
  },

  async mounted() {
    const route = useRoute()
    const orderId = route.query.order_id;
  

    if (!orderId) {
      this.loading = false;
      this.message = "Missing session ID in URL.";
      return;
    }

    try {
      const response = await axios.post(`http://localhost:8000/finalize_order/${orderId}`)
      if (response.status === 200) {
        this.success = true;
      } else {
        this.message = response.data.message || "Unexpected error during finalization.";
      }
    } catch (error) {
      console.error("Finalization error:", error.response?.data || error.message);
    } finally {
      this.loading = false;
    }
  
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
  margin-top: 30px;
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
  font-size: 12px;
}
tfoot td {
  font-weight: bold;
  border-bottom: 2px solid black;
}
.backbtn {
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
