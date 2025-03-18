<template>
  <div class="container">
    <h2>Group Order</h2>
    <p>Cart ID: {{ cartId }}</p>

    <h3>Vendor Menu</h3>
    <div class="menu-items">
      <div v-for="item in menuItems" :key="item.ItemID" class="menu-card">
        <h5>{{ item.ItemName }}</h5>
        <p>${{ item.Price }}</p>
        <button @click="addToSharedCart(item)">Add to Cart</button>
      </div>
    </div>

    <h3>Shared Cart</h3>
    <ul>
      <li v-for="item in sharedCart" :key="item.ID">
        {{ item.ItemName }} - ${{ item.Price }} x {{ item.Quantity }}
        <button @click="removeFromSharedCart(item.ID)">Remove</button>
      </li>
    </ul>

    <p>
      <strong>Total: ${{ totalPrice }}</strong>
    </p>
    <button class="checkout-btn">Checkout</button>
  </div>
</template>

<script>
import { io } from "socket.io-client";
import axios from "axios";

const socket = io("http://localhost:5012");

export default {
  data() {
    return {
      cartId: "",
      vendor: {},
      menuItems: [],
      sharedCart: [],
    };
  },
  async mounted() {
    this.cartId = this.$route.params.cartId;
    await this.fetchCart();
    await this.fetchVendor();
    await this.fetchMenuItems();

    socket.emit("join_cart", { cartId: this.cartId });

    socket.on("cart_updated", (data) => {
      if (data.cartId === this.cartId) {
        this.sharedCart = data.items;
      }
    });
  },
  computed: {
    totalPrice() {
      return this.sharedCart
        .reduce((sum, item) => sum + item.Price * item.Quantity, 0)
        .toFixed(2);
    },
  },
  methods: {
    async fetchCart() {
      try {
        const response = await axios.get(
          `http://localhost:5012/group-order/${this.cartId}`
        );
        this.sharedCart = response.data.items;
      } catch (error) {
        console.error("Error fetching cart:", error);
      }
    },
    async addToSharedCart(item) {
      await axios.post(
        `http://localhost:5012/group-order/${this.cartId}/add-item`,
        {
          userId: localStorage.getItem("user_id"),
          itemId: item.ItemID,
          quantity: 1,
        }
      );
    },
    async removeFromSharedCart(itemId) {
      await axios.delete(
        `http://localhost:5012/group-order/${this.cartId}/remove-item/${itemId}`
      );
    },
    async fetchMenuItems() {
      try {
        const response = await fetch("http://localhost:5002/vendors");
        this.vendors = await response.json();
      } catch (error) {
        console.error("Failed to fetch vendors:", error);
      }
    },
  },
};
</script>
