<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <!-- Brand / Logo -->
      <router-link to="/" class="navbar-brand">yumsinmytums</router-link>

      <!-- Mobile Toggle Button -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navbar Links -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <router-link to="/" class="nav-link">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/about" class="nav-link">About</router-link>
          </li>
          <li v-if="isLoggedIn" class="nav-item">
            <router-link to="/order" class="nav-link">Order</router-link>
          </li>
          <li class="nav-item">
            <router-link v-if="!isLoggedIn" to="/login" class="nav-link"
              >Login</router-link
            >
          </li>
          <button v-if="isLoggedIn" @click="logout">Logout</button>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem("token");
    },
  },
  methods: {
    logout() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  /* background-color: #333; */
  overflow: hidden;
  z-index: 1000;
}
</style>
