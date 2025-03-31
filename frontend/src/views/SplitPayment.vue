<template>
    <div class="split-payment-container">
      <h2>Split Payment Breakdown</h2>
  
      <div v-for="(items, user) in groupBreakdown" :key="user" class="split-user-block">
        <h4>{{ user }}</h4>
        <ul>
          <li v-for="item in items" :key="item.ItemID">
            {{ item.ItemName }} — ${{ item.Price }} x {{ item.Quantity || 1 }}
          </li>
        </ul>
        <p><strong>Total: ${{ getUserTotal(items).toFixed(2) }}</strong></p>
      </div>
  
      <RouterLink :to="'/'" class="backbtn">Return to Home</RouterLink>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        savedCart: [],
      };
    },
    computed: {
      groupBreakdown() {
        const map = {};
        this.savedCart.forEach(item => {
          const user = item.Username || "Unknown";
          if (!map[user]) map[user] = [];
          map[user].push(item);
        });
        return map;
      },
    },
    methods: {
      getUserTotal(items) {
        return items.reduce((sum, item) => sum + item.Price * (item.Quantity || 1), 0);
      },
    },
    mounted() {
      const cart = sessionStorage.getItem("cart");
      this.savedCart = cart ? JSON.parse(cart) : [];
    },
  };
  </script>
  
  <style scoped>
  .split-payment-container {
    max-width: 600px;
    margin: auto;
    padding: 20px;
  }
  .split-user-block {
    margin-bottom: 30px;
  }
  .backbtn, .splitbtn {
    margin-top: 20px;
    display: inline-block;
    padding: 10px 30px;
    background-color: #6495ed;
    color: white;
    border-radius: 8px;
    text-decoration: none;
  }
  </style>
  