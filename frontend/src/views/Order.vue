<template>
  <div class="container">
    <!-- Display message if user is not logged in -->
    <p v-if="!userLoggedIn">Please log in to view vendors and place orders.</p>

    <!-- Display Vendors & Food Items for Logged-in Users -->
    <div v-if="userLoggedIn">
      <div class="row g-3 mx-lg-5 mx-sm-3">
        <!-- <h2>Welcome, {{ user.name }}</h2> -->
         <!-- Recommended Vendors -->
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
              <img
                :src="vendor.ImageURL"
                class="card-img-top"
                alt="Vendor Image"/>
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
export default {
  data() {
    return {
      user: null,
      userLoggedIn: false,
      vendors: [],
      recommendedVendors: [
  //     {
  //   VendorID: 1,
  //   VendorName: "Sushi Express",
  //   Cuisine: "Japanese",
  //   ImageURL: "https://images.unsplash.com/photo-1553621042-f6e147245754" // placeholder sushi image
  // },
  // {
  //   VendorID: 2,
  //   VendorName: "K-BBQ Delight",
  //   Cuisine: "Korean",
  //   ImageURL: "https://images.unsplash.com/photo-1600891963939-a7f8d8e84f92"
  // },
  // {
  //   VendorID: 3,
  //   VendorName: "Mama’s Indian Kitchen",
  //   Cuisine: "Indian",
  //   ImageURL: "https://images.unsplash.com/photo-1613145993487-bc2b2d17f45c"
  // }
      ],
    };
  },
  async mounted() {
    // Check if user is logged in
    const storedUser = localStorage.getItem("token");
    if (storedUser) {
      // this.user = JSON.parse(storedUser);
      this.userLoggedIn = true;
      this.fetchVendors();
      this.fetchRecommendations();
    }
  },
  methods: {
    async fetchVendors() {
      try {
        const response = await fetch("http://localhost:8000/vendors"); // Fetch vendors from backend
        this.vendors = await response.json();
        console.log(this.vendors);
      } catch (error) {
        console.error("Failed to fetch vendors:", error);
      }
    },
    async fetchRecommendations() {
    try {
      // const userId = JSON.parse(atob(localStorage.getItem("token").split('.')[1])).id; // Get userId from JWT
      // const response = await fetch("http://localhost:5013/recommend", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ user_id: userId }),
      // });
      // const data = await response.json();
      // console.log(data);
      // this.recommendedVendors = data.recommended || [];
      // console.log(data.recommended);
      const response = await fetch("http://localhost:5013/recommend", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ user_id: 1 }),
});
const { recommended } = await response.json();

    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
    }
  },
    addToCart(item) {
      const existingItem = this.cart.find(
        (cartItem) => cartItem.id === item.id
      );
      if (existingItem) {
        existingItem.quantity += 1;
      } else {
        this.cart.push({ ...item, quantity: 1 });
      }
    },
    removeFromCart(item) {
      this.cart = this.cart.filter((cartItem) => cartItem.id !== item.id);
    },
    async placeOrder() {
      if (this.cart.length === 0) {
        alert("Your cart is empty.");
        return;
      }

      try {
        const response = await fetch("http://localhost:5001/orders", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({ userId: this.user.id, items: this.cart }),
        });

        const data = await response.json();
        if (response.ok) {
          alert("Order placed successfully!");
          this.cart = []; // Clear cart after successful order
        } else {
          alert(data.message || "Order failed.");
        }
      } catch (error) {
        console.error("Order placement failed:", error);
      }
      
    },

  },
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

.card-title{
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 0;
}

p{
  font-size: 12px;
  color: gray;
  margin-bottom: 0;
}

.vendor-menu{
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
