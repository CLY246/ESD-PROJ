<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();
const amount = ref(0);
const paymentUrl = ref("");

// 👇 Assume these are passed or available
const cart = JSON.parse(localStorage.getItem("cart")) || [];
const userID = localStorage.getItem("user_id") || "";
const vendorName = localStorage.getItem("vendorname") || "";
const cuisine = localStorage.getItem("cuisine") || "";

const createPayment = async () => {
  try {
    // ✅ Auto-calculate total
    amount.value = cart.reduce((sum, item) => {
      const price = parseFloat(item.Price) || 0;
      const qty = parseInt(item.quantity) || 1;
      return sum + price * qty;
    }, 0);

    const response = await axios.post("http://localhost:8000/payments", {
      Amount: amount.value,
    });

    console.log("Stripe response:", response.data);

    if (response.data.paymentUrl && response.data.transaction) {
      const { OrderID, TransactionID, Amount } = response.data.transaction;

      const sanitizedCart = cart.map(item => ({
        ...item,
        ItemID: parseInt(item.ItemID),
        Price: parseFloat(item.Price),
        quantity: parseInt(item.quantity) || 1
      }));

      sessionStorage.setItem(
        "transaction",
        JSON.stringify({
          OrderID: parseInt(OrderID),
          TransactionID: TransactionID,
          Amount: parseFloat(Amount)
        })
      );
      sessionStorage.setItem("cart", JSON.stringify(sanitizedCart));
      sessionStorage.setItem("user_id", userID);
      sessionStorage.setItem("vendorname", vendorName);
      sessionStorage.setItem("cuisine", cuisine);

      paymentUrl.value = response.data.paymentUrl;
      window.location.href = paymentUrl.value;
    } else {
      alert("No payment URL returned.");
    }
  } catch (error) {
    console.error("Payment error:", error);
    alert("Payment failed. Please try again.");
  }
};

</script>


<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-2xl font-semibold mb-4">Make a Payment</h2>
      <input
        type="number"
        v-model="amount"
        placeholder="Enter Amount"
        class="p-2 border border-gray-300 rounded w-full mb-4"
      />
      <button
        @click="createPayment"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Pay Now
      </button>
    </div>
  </div>
</template>
