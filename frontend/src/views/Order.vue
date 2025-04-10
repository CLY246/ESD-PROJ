<template>
  <div class="container">
    <p v-if="!userLoggedIn">Please log in to view vendors and place orders.</p>

    <div class="page-layout">
      <!-- LEFT: RECOMMENDED PANEL -->
      <div class="recommended-panel">
        <h3 class="section-title">Recommended For You 🍽️</h3>
        <div class="recommended-list">
          <div
            v-for="vendor in recommendedVendors"
            :key="'rec-' + vendor.VendorID"
            class="vendor-card"
          >
            <RouterLink :to="'/menu/' + vendor.VendorID" class="vendor-link">
              <div class="vendor-image-wrapper">
                <img :src="vendor.ImageURL" alt="Vendor Image" />
              </div>
              <div class="vendor-info">
                <h4>{{ vendor.VendorName }}</h4>
                <p class="cuisine">{{ vendor.Cuisine }}</p>
                <p class="eta">⏱️ ~30 min</p>
              </div>
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- RIGHT: ALL RESTAURANTS -->
      <div class="all-vendors-section">
        <h2 class="section-title">All Restaurants 🏪</h2>
        <div class="vendor-list-grid">
          <div
            v-for="vendor in vendors"
            :key="vendor.VendorID"
            class="vendor-card"
          >
            <RouterLink :to="'/menu/' + vendor.VendorID" class="vendor-menu">
              <div class="card-img-container">
                <img :src="vendor.ImageURL" class="card-img-top" alt="Vendor Image" />
              </div>
              <div class="card-body">
                <h5 class="card-title">{{ vendor.VendorName }}</h5>
                <p>{{ vendor.Cuisine }}</p>
                <p>⏱️ ~30 min</p>
              </div>
            </RouterLink>
          </div>
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
  }
};
</script>


<style scoped>

.page-layout {
  display: flex;
  align-items: stretch; /* ensure both columns stretch */
  gap: 2rem;
  margin-top: 2rem;
  min-height: 100vh; /* full height */
}

/* === Left Panel: Recommended === */
.recommended-panel {
  flex: 0 0 260px;
  height: 100%; /* full height of the parent layout */
  background: #f7fdf7;
  border: 2px solid #e6f4ea;
  border-radius: 14px;
  padding: 1.2rem 1rem;
  box-shadow: 0 4px 12px rgba(173, 232, 182, 0.15);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* Smaller vendor card for recommendation */
.recommended-panel .vendor-card {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(100, 200, 140, 0.1);
  transition: all 0.2s ease-in-out;
}

.recommended-panel .vendor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(100, 200, 140, 0.15);
}

.recommended-panel .vendor-image-wrapper {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
}

.recommended-panel .vendor-image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease-in-out;
}

.recommended-panel .vendor-card:hover img {
  transform: scale(1.05);
}

.recommended-panel .vendor-info {
  flex-grow: 1;
  text-align: left;
}

.recommended-panel .vendor-info h4 {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
  color: #2d7a42;
}

.recommended-panel .cuisine {
  font-size: 0.75rem;
  color: #666;
}

.recommended-panel .eta {
  font-size: 0.7rem;
  color: #22c55e;
  font-style: italic;
}

/* === Right Panel: All Vendors === */
.all-vendors-section {
  flex: 1;
}

/* General padding for large screens */
@media (min-width: 1440px) {
  .row {
    padding-left: 250px;
    padding-right: 250px;
  }
}

/* ======== RECOMMENDED SECTION ======== */
.recommended-section {
  margin-top: 2rem;
  margin-bottom: 3rem;
  padding: 1rem;
  background: linear-gradient(to right, #f0f4ff, #fefefe);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 1.75rem;
  font-weight: bold;
  color: #4f46e5;
  text-align: center;
  margin-bottom: 2rem;
}

.recommended-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.all-vendors-section .vendor-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
}


/* Optional: force vendor cards in panel to take full width */
.recommended-panel .vendor-card {
  width: 100%;
}

.vendor-link {
  text-decoration: none;
  color: inherit;
  display: block;
}


.cuisine {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.2rem;
}

.eta {
  font-size: 0.85rem;
  color: #10b981;
}

/* ======== DEFAULT VENDOR LIST ======== */
.card {
  border-radius: 12px;
  overflow: hidden;
  background-color: white;
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
}

/* ======== ALL VENDORS GRID LAYOUT ======== */
.vendor-list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
  margin-bottom: 3rem;
}


.card-img-container {
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.card-img-top {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease-in-out;
}

.card-body {
  padding: 16px;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.card-body p {
  font-size: 0.9rem;
  color: gray;
  margin-bottom: 0.2rem;
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
