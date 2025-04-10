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
        <p class="restaurant-meta">{{ vendor.Cuisine }}</p>
        <h1 class="restaurant-title">{{ vendor.VendorName }}</h1>
        <p>Waiting Time: 10 min</p>
        <button class="group-order-btn" @click="startGroupOrder">
          Start Group Order
        </button>
      </div>
    </div>

    <!-- Sticky Category Tabs -->
    <div class="sticky-tabs">
      <div class="category-tabs">
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
    <div class="menu row g-4">
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
                <div class="d-flex justify-content-between align-items-center">
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
                    <button @click="addToCart(item)" class="addtocart">
                      <fa :icon="['fas', 'plus']" style="color: gray"></fa>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="sticky-cart w-100">
          <div class="order-type-toggle">
            <button :class="['tab active']">Pick Up</button>
            <button class="tab disabled" disabled title="Not available yet">
              Delivery
            </button>
          </div>
          <h2 class="fw-bold">Your Cart</h2>

          <!-- Cart Items -->
          <div class="cart-container">
            <div v-if="cart.length === 0" class="text-muted small">
              Your cart is empty.
            </div>
            <div class="cart-items">
              <div
                v-for="item in cart"
                :key="item.ItemID"
                class="cart-mini-card"
              >
                <img :src="item.ImageURL" alt="item" class="cart-mini-img" />
                <div class="cart-mini-details">
                  <p class="cart-mini-title">{{ item.ItemName }}</p>
                  <div class="cart-mini-meta">
                    <span class="cart-mini-price"
                      >${{ item.Price.toFixed(2) }}</span
                    >
                    <span class="cart-mini-qty">1x</span>
                  </div>
                </div>
                <button @click="removeFromCart(item)" class="cart-mini-remove">
                  ×
                </button>
              </div>
            </div>
          </div>

          <!-- Sticky Footer (Total & Payment Button) -->
          <div class="cart-footer">
            <!-- <p class="fw-bold">Total: ${{ totalPrice }}</p> -->
            <div class="cart-summary">
              <div class="summary-row">
                <span>Sub Total</span>
                <span>${{ totalPrice }}</span>
              </div>
              <div class="summary-row">
                <span>Tax 5%</span>
                <span>$0.00</span>
              </div>
              <hr />
              <div class="summary-row total">
                <span>Total Amount</span>
                <span class="fw-bold">${{ totalPrice }}</span>
              </div>
            </div>

            <StripeCheckout
              ref="checkoutRef"
              mode="payment"
              :pk="publishableKey"
              :line-items="lineItems"
              :success-url="successURL.value"
              :cancel-url="cancelURL.value"
              @loading="(v) => (loading = v)"
            />
            <button class="btn placeorder w-100" @click="placeorder">
              Place Order
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import { StripeCheckout } from "@vue-stripe/vue-stripe";

const route = useRoute();
const router = useRouter();
const vendorId = route.params.id;
const vendor = ref({});
const menuItems = ref({});
const cart = ref([]);

const loading = ref(false);

// Stripe Variables
const publishableKey = ref(
  "pk_test_51R2Nh0Bz8bLJBV2o8mzAgS2z1jPVz0RVXTsJLF2lcH6TNpbfiOWNDhqF5it1GN2KkT8n7NUqltpJU7uAx5yIPuyl00umDgnPUu"
);

const successURL = ref("http://localhost:8080/success");
const cancelURL = ref("http://localhost:8080/cancel");

// Compute Line Items for Stripe
const lineItems = computed(() =>
  cart.value.map((item) => ({
    price_data: {
      currency: "sgd",
      product_data: { name: item.ItemName },
      unit_amount: Math.round(item.Price * 100),
    },
    quantity: item.quantity || 1,
  }))
);

const fetchVendor = async () => {
  try {
    const response = await axios.get(
      `http://localhost:8000/vendors/${vendorId}`
    );
    vendor.value = response.data;
  } catch (error) {
    console.error("Error fetching vendor:", error);
  }
};

const fetchMenuItems = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/menu/${vendorId}`);
    menuItems.value = response.data; // Already categorized
  } catch (error) {
    console.error("Error fetching menu items:", error);
  }
};

const startGroupOrder = async () => {
  try {
    const userId = localStorage.getItem("user_id");
    const response = await axios.post(
      "http://localhost:8000/group-order/invite",
      {
        vendorId: vendorId,
        userId: userId,
      }
    );

    const cartId = response.data.cartId;

    localStorage.setItem("shared_cart_id", cartId);

    router.replace(`/group-order/join/${cartId}`);
  } catch (error) {
    console.error("Error starting group order:", error);
  }
};

const placeorder = async () => {
  console.log("Menu.vue: placeorder() triggered");
  try {
    const userID = localStorage.getItem("user_id");

    const cartItems = cart.value.map((item) => ({
      ItemID: parseInt(item.ItemID),
      ItemName: item.ItemName,
      Quantity: parseInt(item.quantity) || 1,
      Price: parseFloat(item.Price) || 0,
      VendorID: parseInt(item.VendorID),
    }));

    const orderData = {
      UserID: userID,
      VendorID: vendorId,
      TotalAmount: parseFloat(totalPrice.value),
      OrderItems: cartItems,
    };

    const response = await axios.post(
      "http://localhost:8000/place_order",
      {
        order: orderData,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (response.data && response.data.paymentUrl) {
      sessionStorage.setItem("isGroupOrder", "false");
      window.location.href = response.data.paymentUrl;
    } else {
      alert("Failed to get payment link.");
    }
  } catch (error) {
    console.error("Order placement error:", error.response?.data || error);
    alert("Failed to place order.");
  }
};

onMounted(() => {
  console.log("MOUNTED: Menu.vue");
  console.trace();
  fetchVendor();
  fetchMenuItems();
});

const addToCart = (item) => {
  const existingItem = cart.value.find((i) => i.ItemID === item.ItemID);
  if (existingItem) {
    existingItem.quantity = (existingItem.quantity || 1) + 1;
  } else {
    cart.value.push({ ...item, quantity: 1 });
  }
};

const removeFromCart = (item) => {
  cart.value = cart.value.filter((i) => i.ItemID !== item.ItemID);
};

const totalPrice = computed(() =>
  cart.value
    .reduce((sum, item) => sum + item.Price * (item.quantity || 1), 0)
    .toFixed(2)
);

const scrollToCategory = (id) => {
  document.getElementById(id).scrollIntoView({ behavior: "smooth" });
};
</script>

<style scoped>
/* Ensure smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Layout */
.container {
  margin-top: 70px;
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

@media (min-width: 1440px) {
  .restaurant-info,
  .menu {
    padding-left: 150px;
    padding-right: 150px;
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
  border: 1px solid #097d4c;
  transform: scale(1.05);
}

/* Sticky Full-Height Cart */
.sticky-cart {
  display: flex;
  flex-direction: column;
  height: 100vh; /* or set this to fit your layout */
  border-left: 2px solid #e0e0e0;
  padding: 16px;
  box-sizing: border-box;
}

.order-type-toggle {
  display: flex;
  background-color: #f5f5f5;
  border-radius: 40px;
  overflow: hidden;
  width: 100%;
  height: 50px;
  margin-bottom: 20px;
}

.order-type-toggle .tab {
  padding: 10px 20px;
  border: none;
  background-color: transparent;
  font-weight: bold;
  color: #333;
  cursor: pointer;
  transition: 0.2s ease-in-out;
  flex: 1;
}

.order-type-toggle button.tab.active {
  background-color: #b5dfb2 !important;
  color: #333;
  border-radius: 40px;
}

.order-type-toggle .tab.disabled {
  background-color: #eee;
  color: #ccc;
  cursor: not-allowed;
}

/* Scrollable Cart Items */
.cart-container {
  flex-grow: 1;
  overflow-y: auto;
  max-height: calc(100vh - 150px); /* Adjust height dynamically */
}

.cart-mini-card {
  display: flex;
  align-items: center;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 10px;
  margin-bottom: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.cart-mini-img {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  object-fit: cover;
  margin-right: 12px;
}

.cart-mini-details {
  flex-grow: 1;
}

.cart-mini-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px;
  color: #333;
}

.cart-mini-meta {
  display: flex;
  gap: 10px;
  align-items: center;
}

.cart-mini-price {
  font-size: 13px;
  font-weight: bold;
  color: #097d4c;
}

.cart-mini-qty {
  font-size: 13px;
  color: #888;
}

.cart-mini-remove {
  border: none;
  background: transparent;
  color: #999;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  padding: 0 10px;
  transition: color 0.2s;
}

.cart-mini-remove:hover {
  color: #e74c3c;
}

.cart-summary {
  background: #f9f9f9;
  padding: 16px;
  border-top: 1px solid #ddd;
  border-radius: 16px 16px 0 0;
  margin-bottom: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 14px;
  color: #333;
}

.summary-row.total {
  font-weight: bold;
  font-size: 15px;
  margin-top: 8px;
}

.placeorder {
  background-color: #097d4c;
  text-align: center;
  color: #fff;
}

/* Sticky Footer */
.cart-footer {
  position: sticky;
  bottom: 0;
  background: white;
  padding: 10px 0;
  border-top: 1px solid #ddd;
}
.group-order-btn {
  border-radius: 25px;
  padding: 10px 20px;
  border: 0;
}
</style>
