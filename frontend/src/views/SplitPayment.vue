<template>
  <div class="split-container">
    <h2 class="total-title">💳 Total Bill</h2>
    <p class="total-amount">${{ totalAmount }}</p>

    <div class="user-grid">
      <div v-for="(items, user) in groupBreakdown" :key="user" class="user-card">
        <div class="user-header">
          <h3>{{ user }}</h3>
          <span class="user-total">${{ getUserTotal(items) }}</span>
        </div>

        <!-- Progress bar -->
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: getUserPercentage(items) + '%' }"
          ></div>
        </div>
        <p class="user-percent">{{ getUserPercentage(items) }}%</p>

        <!-- Items -->
        <div class="item-list">
          <div
            v-for="item in items"
            :key="item.ItemID"
            class="item-entry"
          >
            <span class="item-name">{{ item.ItemName }}</span>
            <span class="item-cost">
              ${{ item.Price }} x {{ item.Quantity || 1 }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <router-link to="/" class="back-link">⬅️ Return to Home</router-link>
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
    totalAmount() {
      return Object.values(this.groupBreakdown)
        .flat()
        .reduce((sum, item) => sum + item.Price * (item.Quantity || 1), 0)
        .toFixed(2);
    },
  },
  methods: {
    getUserTotal(items) {
      return items.reduce((sum, item) => sum + item.Price * (item.Quantity || 1), 0).toFixed(2);
    },
    getUserPercentage(items) {
      const total = parseFloat(this.totalAmount);
      const userTotal = items.reduce((sum, item) => sum + item.Price * (item.Quantity || 1), 0);
      return total > 0 ? ((userTotal / total) * 100).toFixed(1) : 0;
    },
  },
  mounted() {
    const cart = sessionStorage.getItem("cart");
    this.savedCart = cart ? JSON.parse(cart) : [];
  },
};
</script>


<style scoped>
.split-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
  text-align: center;
  font-family: 'Segoe UI', sans-serif;
}

.total-title {
  font-size: 2.5rem;
  color: #4f46e5; /* Indigo */
  margin-bottom: 0.5rem;
}

.total-amount {
  font-size: 3rem;
  font-weight: bold;
  color: #1e1e2f;
  margin-bottom: 2rem;
}

.user-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}

.user-card {
  flex: 1 1 calc(25% - 20px); /* 4 per row max */
  background-color: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 1rem;
  min-width: 250px;
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.user-total {
  font-size: 1.5rem;
  font-weight: bold;
  color: #10b981;
  border-bottom: 2px solid #d1d5db;
  padding-bottom: 4px;
  margin-bottom: 10px;
}



.progress-bar {
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(to right, #7c3aed, #3b82f6);
  transition: width 0.3s ease-in-out;
}

.user-percent {
  text-align: right;
  font-size: 0.75rem;
  color: #888;
  margin-bottom: 0.5rem;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
}

.item-entry {
  display: flex;
  justify-content: space-between;
  background-color: #ffffff;
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.9rem;
}

.back-link {
  display: inline-block;
  margin-top: 2rem;
  color: #4f46e5;
  text-decoration: none;
  font-size: 0.9rem;
}

.back-link:hover {
  text-decoration: underline;
}

</style>
