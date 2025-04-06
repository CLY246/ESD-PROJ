<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { jwtDecode } from "jwt-decode"; 

const router = useRouter();

const amount = ref(0);
const paymentUrl = ref("");

// Retrieve from session storage (cart info)
const cart = JSON.parse(sessionStorage.getItem("cart")) || [];
const vendorName = cart[0]?.VendorName || cart[0]?.vendor_name || "Vendor";
const cuisine = cart[0]?.Cuisine || cart[0]?.cuisine || "Unknown";

// Retrieve userID explicitly from local storage
let userID = localStorage.getItem("user_id") || "";
if (!userID) {
  const token = localStorage.getItem("token");
  if (token) {
    try {
      const decoded = jwtDecode(token);
      userID = decoded.UserID || decoded.user_id || decoded.sub;
      localStorage.setItem("user_id", userID); // Save explicitly in local storage
    } catch (error) {
      console.error("JWT decode failed:", error);
      alert("Authentication error. Please log in again.");
      router.push('/');
    }
  } else {
    alert("User not authenticated. Redirecting to home.");
    router.push('/');
  }
}

const createPayment = async () => {
  try {
    if (!cart.length) {
      alert("Your cart is empty.");
      router.push('/');
      return;
    }

    // Calculate total amount from cart
    amount.value = cart.reduce((sum, item) => {
      const price = parseFloat(item.Price) || 0;
      const qty = parseInt(item.quantity) || 1;
      return sum + price * qty;
    }, 0);

    // Trigger payment via backend API
    const response = await axios.post("http://localhost:8000/trigger_payment", {
      UserID: userID,
      VendorID: parseInt(cart[0].VendorID),
      TotalAmount: amount.value,
      OrderItems: cart.map(item => ({
        ItemID: parseInt(item.ItemID),
        ItemName: item.ItemName,
        Quantity: parseInt(item.quantity) || 1,
        Price: parseFloat(item.Price)
      }))
    });

    console.log("Stripe response:", response.data);

    if (response.data.paymentUrl && response.data.transaction) {
      const { OrderID, TransactionID, Amount } = response.data.transaction;

      // Prepare sanitized cart for success page
      const sanitizedCart = cart.map(item => ({
        ItemID: parseInt(item.ItemID),
        ItemName: item.ItemName,
        Price: parseFloat(item.Price),
        quantity: parseInt(item.quantity) || 1,
        VendorID: parseInt(item.VendorID),
        ImageURL: item.ImageURL || ""
      }));

      sessionStorage.setItem("transaction", JSON.stringify({
        OrderID: parseInt(OrderID),
        TransactionID: TransactionID,
        Amount: parseFloat(Amount),
        paymentUrl: response.data.paymentUrl
      }));
      sessionStorage.setItem("cart", JSON.stringify(sanitizedCart));
      sessionStorage.setItem("vendorname", vendorName);
      sessionStorage.setItem("cuisine", cuisine);
      sessionStorage.setItem("isGroupOrder", "true");

      // ✅ Update the recommendation model with the ordered cuisine
      try {
        await axios.post("http://localhost:5013/update_model", {
          cuisine: cuisine  // This comes from session or cart, like "Thai", "Japanese"
        });
        console.log("Model updated with cuisine:", cuisine);
      } catch (err) {
        console.error("Failed to update model with cuisine:", err);
      }


      console.log("Session Storage before Stripe redirect:", {
        userID,
        cart: sanitizedCart,
        vendorName,
        cuisine
      });

      // Redirect to Stripe Checkout
      window.location.href = response.data.paymentUrl;

    } else {
      alert("No payment URL returned from the server.");
      router.push('/');
    }
  } catch (error) {
    console.error("Payment error:", error);
    alert("Payment failed. Please try again.");
    router.push('/');
  }
};

onMounted(() => {
  const transaction = JSON.parse(sessionStorage.getItem("transaction"));

  if (transaction?.paymentUrl) {
    console.log("Redirecting to existing payment URL:", transaction.paymentUrl);
    window.location.href = transaction.paymentUrl;
  } else {
    createPayment();
  }
});
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
