<template>
  <div>
    <router-view></router-view>
    <!-- <h1>Vue.js + Flask + Docker</h1>
    <p>{{ message }}</p>

    <h2>Users</h2>
    <p v-if="users.length === 0">Loading users...</p>
    <ul>
      <li v-for="user in users" :key="user.id">{{ user.name }} - {{ user.email }}</li>
    </ul> -->
  </div>
  
</template>

<!-- <script>
export default {
  data() {
    return {
      users: [],
    };
  },
  async mounted() {
    const userApi = import.meta.env.VITE_USER_API || "http://localhost:5001/api/users";
   
    console.log("Fetching from APIs:", userApi);

    try {
      const userResponse = await fetch(userApi);
      this.users = await userResponse.json();

    } catch (error) {
      console.error("API request failed:", error);
    }
  }
};
</script>
 -->

