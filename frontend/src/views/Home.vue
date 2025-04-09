<template>
  <div class="container">
    <div class="row align-items-center">
      <!-- Left Side (Text) -->
      <div class="col-md-4 left">
        <h1 class="display-5 fw-bold mb-3">
          Hungry? You're in the right place
        </h1>
        <p class="subtext">
          Vestibulum rutrum quam vitae fringilla tincidunt. Suspendisse nec
          tortor urna. Ut laoreet sodales nisi, quis iaculis nulla iaculis
          vitae.
        </p>
        <button class="btn btn-lg mt-3" @click="goToVendors">Find Restaurant</button>
      </div>

      <div class="col-md-8 position-relative mt-4 mt-md-0 text-center">
        <img
          src="https://i.pinimg.com/736x/24/13/c8/2413c86a97bba25da31a9c0f28f6d351.jpg"
        />
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      userLoggedIn: false,
    };
  },
  async mounted() {
    const storedUser = localStorage.getItem("token");
    if (storedUser) {
      this.userLoggedIn = true;
    }
  },
  methods: {
    goToVendors() {
      if (this.userLoggedIn) {
        this.$router.push("/order");
      } else {
        this.$router.push("/login");
      }
    },
  },
};
</script>

<style scoped>
.container {
  padding-left: 150px;
  padding-top: 70px;
}
.main-illustration {
  max-width: 80%;
}
.btn {
  background-color: #bfbfae;
  border: none;
  padding: 10px 50px;
  border-radius: 20px;
  transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.btn:hover {
  transform: scale(1.1);
  background-color: #bfbfae;
  border: none;
}
h1 {
  max-width: 500px;
}
.subtext {
  font-size: 14px;
}
</style>
