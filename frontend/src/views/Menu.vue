<template>
    <div class="container">
      <h2>Menu for Vendor {{ vendorId }}</h2>
      <!-- Display vendor menu items here -->
    </div>
  </template>
  
  <script setup>
  import { useRoute } from "vue-router";
  
  const route = useRoute();
  const vendorId = route.params.id;
  </script>
  