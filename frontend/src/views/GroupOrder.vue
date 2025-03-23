<template>
  <div class="container">
    <!-- Restaurant Info Section -->
    <div class="restaurant-info">
      <img
        :src="vendor.ImageURL"
        alt="Restaurant Image"
        class="restaurant-img"
      />
      <div>
        <p>Cart ID: {{ cartId }}</p>
        <p class="restaurant-meta">{{ vendor.Cuisine }}</p>
        <h1 class="restaurant-title">{{ vendor.VendorName }}</h1>
        <p>Waiting Time: 30 min</p>
        <p class="restaurant-rating">⭐ {{ vendor.Rating }}</p>
      </div>
    </div>

    <!-- Sticky Category Tabs -->
    <div class="sticky-tabs">
      <div class="category-tabs">
        <div v-if="menuItems">
          <button
            v-for="(items, category) in menuItems"
            :key="category"
            @click="scrollToCategory(category)"
            class="category-button"
          >
            {{ category }}
          </button>
        </div>
      </div>

      <!-- Menu Layout -->
      <div class="row g-4">
        <!-- Menu Items Section -->
        <div class="col-lg-8">
          <div
            v-for="(items, category) in menuItems"
            :key="category"
            :id="category"
            class="mb-4"
          >
            <h2 class="fw-bold mb-3">{{ category }}</h2>
            <div class="row g-3">
              <div v-for="item in items" :key="item.ItemID" class="col-md-6">
                <div class="card shadow-sm p-3">
                  <div
                    class="d-flex justify-content-between align-items-center"
                  >
                    <div>
                      <h5>{{ item.ItemName }}</h5>
                      <p class="description text-muted small">
                        {{ item.Description }}
                      </p>
                      <p>${{ item.Price.toFixed(2) }}</p>
                    </div>
                    <div class="item-img">
                      <img
                        :src="item.ImageURL"
                        alt="Item Image"
                        class="menu-item-img rounded"
                      />
                      <button @click="addToSharedCart(item)" class="addtocart">
                        <fa :icon="['fas', 'plus']" style="color: gray"></fa>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Cart Section: Move this inside the same row -->
        <div class="col-lg-4">
          <div class="sticky-cart w-100">
            <h2 class="fw-bold">Your Cart</h2>

            <!-- Cart Items -->
            <div class="cart-items">
              <div v-if="sharedCart.length === 0" class="text-muted small">
                Your cart is empty.
              </div>

              <!-- Loop through each user -->
              <div v-for="(items, username) in groupedCart" :key="username">
                <h3 class="fw-bold">{{ username }}</h3>
                <!-- Display Username -->

                <ul>
                  <li v-for="item in items" :key="item.ID">
                    {{ item.ItemName }} - ${{ item.Price }} x
                    {{ item.Quantity }}
                    <button @click="removeFromSharedCart(item.ID)">
                      Remove
                    </button>
                  </li>
                </ul>
              </div>

              <p>
                <strong>Total: ${{ totalPrice }}</strong>
              </p>
            </div>

            <!-- Sticky Footer (Total & Payment Button) -->
            <div class="cart-footer">
              <p class="fw-bold">Total: ${{ totalPrice }}</p>
              <button class="btn btn-dark w-100">
                Review Payment and Address
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  "https://ioskwqelrdcangizpzij.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlvc2t3cWVscmRjYW5naXpwemlqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIwNTc0NTksImV4cCI6MjA1NzYzMzQ1OX0.Kpt-FzHu9yA7ilcCmSRYtPcHtjnei276B-uIZx_4cxc"
);

export default {
  data() {
    return {
      cartId: "",
      vendor: {},
      menuItems: {},
      sharedCart: [],
      channel: null,
    };
  },
  mounted() {
    this.cartId = this.$route.params.cartId;

    if (!this.cartId) {
      console.error("cartId not found in route params");
      return;
    }

    console.log("cartId:", this.cartId);
    this.fetchVendorFromCart();
    this.fetchSharedCart();
    this.subscribeToCartUpdates();
  },
  beforeUnmount() {
    if (this.channel) {
      supabase.removeChannel(this.channel);
    }
  },
  computed: {
    totalPrice() {
      return Array.isArray(this.sharedCart)
        ? this.sharedCart
            .reduce((sum, item) => sum + (item.Price * item.Quantity || 0), 0)
            .toFixed(2)
        : "0.00";
    },
    groupedCart() {
      return this.sharedCart.reduce((acc, item) => {
        if (!acc[item.Username]) acc[item.Username] = [];
        acc[item.Username].push(item);
        return acc;
      }, {});
    },
  },
  methods: {
    subscribeToCartUpdates() {
      console.log("Subscribing to Supabase realtime for cart:", this.cartId);
      this.channel = supabase
        .channel("cart-realtime")
        .on(
          "postgres_changes",
          {
            event: "*",
            schema: "public",
            table: "cart_items",
            filter: `Cart_ID=eq.${this.cartId}`,
          },
          async (payload) => {
            console.log("Realtime update received:", payload);
            await this.fetchSharedCart();
          }
        )
        .subscribe();
    },

    async fetchSharedCart() {
      if (!this.cartId) return;
      try {
        const { data } = await axios.get(
          `http://localhost:8000/group-order/${this.cartId}`
        );

        let cartItems = data.Items || [];
        console.log("Cart Items:", cartItems);

        const itemPromises = cartItems.map(async (item) => {
          try {
            const [menuRes, userRes] = await Promise.all([
              axios.get(`http://localhost:8000/menuitem/${item.Item_ID}`),
              axios.get(`http://localhost:8000/username/${item.User_ID}`),
            ]);
            return {
              ...item,
              ...menuRes.data,
              Username: userRes.data.Username || "Unknown User",
            };
          } catch (err) {
            console.error("Failed to fetch item/user details:", err);
            return {
              ...item,
              ItemName: "Unknown Item",
              Price: 0.0,
              ImageURL: "",
              Username: "Unknown User",
            };
          }
        });

        this.sharedCart = await Promise.all(itemPromises);
      } catch (err) {
        console.error("Error fetching cart:", err);
      }
    },

    async addToSharedCart(item) {
      if (!this.cartId || !item?.ItemID) {
        console.warn("Missing cartId or itemId");
        return;
      }

      try {
        const response = await axios.post(
          `http://localhost:8000/group-order/${this.cartId}/add-item`,
          {
            userId: localStorage.getItem("user_id"),
            itemId: item.ItemID,
            quantity: 1,
          }
        );
        console.log("Item added:", response.data);

        await this.fetchSharedCart();
      } catch (error) {
        this.logAxiosError(error, "adding item");
      }
    },
    async removeFromSharedCart(itemId) {
      if (!this.cartId || !itemId) {
        console.warn("Missing cartId or itemId");
        return;
      }

      try {
        const response = await axios.delete(
          `http://localhost:8000/group-order/${this.cartId}/remove-item/${itemId}`
        );
        console.log("Item removed:", response.data);

        await this.fetchSharedCart();
      } catch (error) {
        this.logAxiosError(error, "removing item");
      }
    },

    async fetchVendorFromCart() {
      try {
        const response = await axios.get(
          `http://localhost:8000/group-order/${this.cartId}/vendor`
        );
        const vendorId = response.data.vendorId;
        console.log("Vendor ID from cart:", vendorId);
        await this.fetchMenuItems(vendorId);
      } catch (error) {
        this.logAxiosError(error, "fetching vendor");
      }
    },

    async fetchMenuItems(vendorId) {
      try {
        const response = await axios.get(
          `http://localhost:8000/menu/${vendorId}`
        );
        this.menuItems = response.data;
      } catch (error) {
        this.logAxiosError(error, "fetching menu items");
      }
    },

    logAxiosError(error, context) {
      if (error.response) {
        console.error(`Error ${context}:`);
        console.log("URL:", error.config.url);
        console.log("Method:", error.config.method);
        console.log("Status:", error.response.status);
        console.log("Data:", error.response.data);
      } else {
        console.error("Network error or unknown:", error.message);
      }
    },
  },
};
</script>

<style scoped>
/* Ensure smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Layout */
.container {
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
}

/* Restaurant Info */
.restaurant-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 30px;
  border-bottom: 1px solid #ddd;
}

@media (min-width: 1600px) {
  .restaurant-info,
  .menu {
    padding-left: 250px;
    padding-right: 250px;
  }
}

.restaurant-img {
  width: 136px;
  height: 136px;
  border-radius: 10px;
  object-fit: cover;
}

.restaurant-title {
  font-size: 30px;
  font-weight: bold;
}

.restaurant-meta {
  color: #666;
}

.restaurant-rating {
  font-size: 14px;
  color: #ff5722;
}

.restaurant-info p {
  font-size: 14px;
  color: gray;
  margin: 5px;
}

/* Sticky Category Tabs */
.sticky-tabs {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: white;
  padding: 10px 0;
  margin-bottom: 20px;

  /* Shadow effect for depth */
  box-shadow: 0 4px 6px -2px rgba(0, 0, 0, 0.1),
    0 10px 15px -3px rgba(0, 0, 0, 0.05);
}

/* Tabs container */
.category-tabs {
  display: flex;
  justify-content: center;
  gap: 16px;
  overflow-x: auto;

  /* Smooth scrolling */
  scroll-behavior: smooth;
}

/* Individual category buttons */
.category-button {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  background: none;
  color: #666;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease-in-out;
}

/* Hover and active state */
.category-button:hover,
.category-button:focus {
  color: black;
  border-bottom: 2px solid black;
}

/* Optional: Add subtle fading on both edges for better scrolling UX */
.category-tabs::before,
.category-tabs::after {
  content: "";
  position: absolute;
  top: 0;
  width: 30px;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.category-tabs::before {
  left: 0;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 1),
    rgba(255, 255, 255, 0)
  );
}

.category-tabs::after {
  right: 0;
  background: linear-gradient(
    to left,
    rgba(255, 255, 255, 1),
    rgba(255, 255, 255, 0)
  );
}

h2 {
  font-size: 16px;
}
h5 {
  font-size: 14px;
}
.description {
  font-size: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
  word-wrap: break-word;
  line-height: 1.4em;
  max-height: 2.8em;
  min-height: 2.8em;
}
.item-img {
  margin-left: 10px;
  width: 100px;
  height: 100px;
}

.menu-item-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  position: relative;
}

.addtocart {
  border-radius: 50px;
  height: 30px;
  width: 30px;
  background-color: white;
  border: none;
  position: absolute;
  right: 19px;
  bottom: 27px;
}

.card:hover {
  background-color: lightgoldenrodyellow;
  transform: scale(1.05);
}

/* Sticky Full-Height Cart */
.sticky-cart {
  position: sticky;
  top: 40px;
  height: 80vh; /* Full height */
  display: flex;
  flex-direction: column;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
  overflow: hidden; /* Prevents overflow */
}

/* Scrollable Cart Items */
.cart-items {
  flex-grow: 1;
  overflow-y: auto;
  max-height: calc(100vh - 150px); /* Adjust height dynamically */
}

/* Sticky Footer */
.cart-footer {
  position: sticky;
  bottom: 0;
  background: white;
  padding: 10px 0;
  border-top: 1px solid #ddd;
}
</style>
