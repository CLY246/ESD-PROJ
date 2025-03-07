<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();
const amount = ref(0);
const paymentUrl = ref("");

const createPayment = async () => {
  try {
    const response = await axios.post("https://your-outsystems-app.com/api/payments", {
      amount: amount.value,
      currency: "USD",
      userId: 123, // Replace with actual user ID
    });

    if (response.data.paymentUrl) {
      paymentUrl.value = response.data.paymentUrl;
      window.location.href = paymentUrl.value; // Redirect to the payment gateway
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
