<template>
    <div>
  
      <h1>Food Ordering System</h1>
  
      <!-- Display message if user is not logged in -->
      <p v-if="!userLoggedIn">Please log in to view vendors and place orders.</p>
  
      <!-- Display Vendors & Food Items for Logged-in Users -->
      <div v-if="userLoggedIn">
        <h2>Welcome, {{ user.name }}</h2>
        <h3>Select Food Items</h3>
  
        <div v-if="vendors.length === 0">
          <p>Loading vendors...</p>
        </div>
  
        <div v-for="vendor in vendors" :key="vendor.VendorID">
            
          <h3>{{ vendor.VendorID }}</h3>
          <!-- <ul>
            <li v-for="item in vendor.menu" :key="item.id">
              {{ item.name }} - ${{ item.price }}
              <button @click="addToCart(item)">Add to Cart</button>
            </li>
          </ul> -->
        </div>

        <!-- Cart Section -->
        <div v-if="cart.length > 0">
          <h3>Cart</h3>
          <ul>
            <li v-for="item in cart" :key="item.id">
              {{ item.name }} - {{ item.quantity }}x (${{ item.price * item.quantity }})
              <button @click="removeFromCart(item)">Remove</button>
            </li>
          </ul>
          <button @click="placeOrder">Place Order</button>
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
        cart: [],
      };
    },
    async mounted() {
      // Check if user is logged in
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        this.user = JSON.parse(storedUser);
        this.userLoggedIn = true;
        this.fetchVendors();
        console.log(this.vendors)
      }
    },
    methods: {
      async fetchVendors() {
        try {
          const response = await fetch("http://localhost:5002/vendors"); // Fetch vendors from backend
          this.vendors = await response.json();
        } catch (error) {
          console.error("Failed to fetch vendors:", error);
        }
      },
      addToCart(item) {
        const existingItem = this.cart.find((cartItem) => cartItem.id === item.id);
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
  .vendor-card {
    border: 1px solid #ccc;
    padding: 10px;
    margin: 10px 0;
  }
  </style>
  