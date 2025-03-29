<template>
    <Navbar v-if="showNavbar" />
    <router-view class="router-container" />
</template>

<script>
import Navbar from "./components/Navbar.vue";
import { useRoute } from "vue-router";
import { computed } from "vue";

export default {
  components: {
    Navbar,
  },
  setup() {
    const route = useRoute();

    // Define exact routes where navbar should be hidden
    const hideNavbarRoutes = ["/login", "/success"];

    // Compute if navbar should be shown
    const showNavbar = computed(() => {
      return !hideNavbarRoutes.includes(route.path) && !route.path.startsWith("/menu/");
    });

    return { showNavbar };
  },
};
</script>


<style>
#app {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.router-container {
  flex: 1; /* Ensures it expands to fill space */
  min-width: 100%;
  padding-top: 20px;
}

*{
  font-family: "Poppins", sans-serif;
}
</style>
