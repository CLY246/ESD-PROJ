<template>
  <div class="container">
    <p v-if="!userLoggedIn">Please log in to view vendors and place orders.</p>

    <div v-if="userLoggedIn">
      <div class="row g-3 mx-lg-5 mx-sm-3">
        <div v-if="recommendedVendors.length > 0" class="mt-4 mb-5">
          <h3>Recommended For You 🍽️</h3>
          <div class="row g-3">
            <div
              v-for="vendor in recommendedVendors"
              :key="'rec-' + vendor.VendorID"
              class="col-lg-4 col-md-6"
            >
              <RouterLink :to="'/menu/' + vendor.VendorID" class="vendor-menu">
                <div class="vendor-card card">
                  <div class="card-img-container">
                    <img :src="vendor.ImageURL" class="card-img-top" />
                  </div>
                  <div class="card-body">
                    <h5 class="card-title">{{ vendor.VendorName }}</h5>
                    <p>{{ vendor.Cuisine }}</p>
                    <p>30 min</p>
                  </div>
                </div>
              </RouterLink>
            </div>
          </div>
        </div>

        <h2>All restaurants</h2>
        <div
          v-for="vendor in vendors"
          :key="vendor.VendorID"
          class="col-lg-4 col-md-6 col-sm-6"
        >
          <RouterLink :to="'/menu/' + vendor.VendorID" class="vendor-menu">
            <div class="vendor-card card">
              <div class="card-img-container">
                <img :src="vendor.ImageURL" class="card-img-top" alt="Vendor Image" />
              </div>
              <div class="card-body">
                <h5 class="card-title">{{ vendor.VendorName }}</h5>
                <p>{{ vendor.Cuisine }}</p>
                <p>30 min</p>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { jwtDecode } from "jwt-decode";

export default {
  data() {
    return {
      user: null,
      userLoggedIn: false,
      vendors: [],
      recommendedVendors: [],
      cart: []
    };
  },

  async mounted() {
    const storedUser = localStorage.getItem("token");
    if (storedUser) {
      this.userLoggedIn = true;
      const decoded = jwtDecode(storedUser);
      const userID = decoded.UserID || decoded.user_id || decoded.sub;
      this.fetchVendors();
      this.fetchAndProcessOrderHistory(userID);
    }
  },

  methods: {
    async fetchVendors() {
      try {
        const response = await fetch("http://localhost:8000/vendors");
        this.vendors = await response.json();
        console.log(this.vendors);
      } catch (error) {
        console.error("Failed to fetch vendors:", error);
      }
    },

    async fetchAndProcessOrderHistory(userID) {
      try {
        const orderHistoryResponse = await fetch(`https://personal-aefq3pkb.outsystemscloud.com/OrderManagement/rest/OrderHistory/getHistory/${userID}`);
        if (!orderHistoryResponse.ok) throw new Error("Failed to fetch order history");

        const orderHistoryData = await orderHistoryResponse.json();
       
        const details = orderHistoryData.UserOrdersAPI.OrderDetails;
        console.log("Order History Data:", details);

        if (Array.isArray(details)) {
          const recommendationsResponse = await fetch("http://localhost:5013/recommendation", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ OrderHistory: details })
          });

          if (!recommendationsResponse.ok) throw new Error("Failed to send data to recommendations API");

          const recommendationsResult = await recommendationsResponse.json();
          this.recommendedVendors = recommendationsResult.recommended;
          console.log("Raw recommendation API result:", recommendationsResult);
          console.log("Recommendations:", recommendationsResult);
        } else {
          console.error("Order history response is not an array");
        }
      } catch (error) {
        console.error("Error processing order history:", error);
      }
    },

    addToCart(item) {
      try {
        console.log("🛒 Adding item:", JSON.stringify(item));
      } catch (e) {
        console.log("🛒 Adding item (raw):", item);
      }

      const existingItem = this.cart.find(cartItem => cartItem.ItemID === item.ItemID);
      if (existingItem) {
        existingItem.quantity += 1;
      } else {
        this.cart.push({ ...item, quantity: 1 });
      }
    },

    removeFromCart(item) {
      this.cart = this.cart.filter(cartItem => cartItem.ItemID !== item.ItemID);
    },

    async placeOrder() {
      if (this.cart.length === 0) return alert("Cart is empty");

      const token = localStorage.getItem("token");
      if (!token) return alert("User not authenticated");

      let userID;
      try {
        const decoded = jwtDecode(token);
        console.log("🚨 Decoded JWT token:", decoded);
        userID = decoded.UserID || decoded.user_id || decoded.sub;

        if (!userID) throw new Error("userID not present in token");
      } catch (error) {
        console.error("❌ JWT decoding failed:", error);
        alert("Invalid or expired user session. Please log in again.");
        return;
      }

      localStorage.setItem("user_id", userID); // ✅ Now using localStorage
      console.log("✅ Saved userID to localStorage:", userID);

      const firstItem = this.cart[0];
      if (!firstItem || !firstItem.VendorID) {
        return alert("Vendor information is missing from cart items.");
      }

      const vendorId = firstItem.VendorID;
      const vendorName = firstItem.VendorName ?? "Vendor";
      const cuisine = firstItem.Cuisine ?? "Unknown";

      const totalAmount = this.cart.reduce((sum, item) => {
        const qty = item.quantity ?? 1;
        const price = parseFloat(item.Price) || 0;
        return sum + price * qty;
      }, 0);

      const orderPayload = {
        UserID: userID,
        VendorID: parseInt(vendorId),
        TotalAmount: totalAmount,
        OrderItems: this.cart
          .filter(item => item.ItemID && item.Price !== undefined)
          .map(item => ({
            ItemID: parseInt(item.ItemID),
            ItemName: item.ItemName ?? "Unnamed Item",
            Quantity: parseInt(item.quantity) || 1,
            Price: parseFloat(item.Price) || 0
          }))
      };

      console.log("🚀 Sending order payload to trigger_payment:", orderPayload);

      try {
        const response = await fetch("http://localhost:8000/trigger_payment", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(orderPayload),
        });

        const data = await response.json();
        console.log("💳 Payment trigger response:", data);

        const paymentUrl = data?.paymentUrl;

        if (response.ok && typeof paymentUrl === "string") {
          sessionStorage.setItem("cart", JSON.stringify(this.cart));
          sessionStorage.setItem("vendorname", vendorName);
          sessionStorage.setItem("cuisine", cuisine);
          sessionStorage.setItem("isGroupOrder", "true");

          sessionStorage.setItem("transaction", JSON.stringify({
            Amount: totalAmount,
            OrderID: data.OrderID,
            TransactionID: data.TransactionID,
            paymentUrl: paymentUrl,
          }));

          console.log("🚨 DEBUG: Storage data before payment redirect:", {
            user_id: userID,
            vendorname: vendorName,
            cuisine: cuisine,
            cart: this.cart
          });

          window.location.href = paymentUrl;
        } else {
          console.error("Payment failed or invalid Stripe URL:", data);
          alert("Payment failed: " + (data.message || data.error || "Unknown error"));
        }
      } catch (error) {
        console.error("Payment request failed:", error);
        alert("Could not initiate payment.");
      }
    }

  }
};
</script>


<style scoped>
@media (min-width: 1600px) {
  .row {
    padding-left: 250px;
    padding-right: 250px;
  }
}
.vendor-card {
  width: 100%;
  height: auto;
  border-radius: 16px;
  overflow: hidden;
  background-color: white;
}

.card-img-container {
  position: relative;
  width: 100%;
  height: 210px;
  overflow: hidden;
  border-radius: 16px 16px 0 0;
}

.card-img-top {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 16px 16px 0 0;
  transition: transform 0.3s ease-in-out;
}

.card-body {
  padding: 16px;
  text-align: left;
}

.vendor-card:hover .card-img-top {
  transform: scale(1.1);
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 0;
}

p {
  font-size: 12px;
  color: gray;
  margin-bottom: 0;
}

.vendor-menu {
  text-decoration: none;
  color: inherit;
  display: block;
}

.vendor-menu:focus,
.vendor-menu:hover {
  outline: none !important;
  border: none !important;
}
</style>
