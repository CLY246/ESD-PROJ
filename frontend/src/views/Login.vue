<template>
  <div class="auth-container">
    <h2>{{ isLogin ? "Login" : "Sign Up" }}</h2>

    <form @submit.prevent="handleSubmit">
      <input v-if="!isLogin" type="text" v-model="name" placeholder="Full Name" required />
      <input v-if="!isLogin" type="text" v-model="username" placeholder="Username" required />
      <input type="text" v-model="identifier" placeholder="Email or Username" required />
      <input type="password" v-model="password" placeholder="Password" required />
      
      <button type="submit" :disabled="loading">{{ isLogin ? "Login" : "Sign Up" }}</button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>

    <p @click="toggleMode" class="toggle">
      {{ isLogin ? "Don't have an account? Sign Up" : "Already have an account? Login" }}
    </p>
  </div>
</template>

<script>
import { loginUser, registerUser } from "@/services/authService";

export default {
  data() {
    return {
      isLogin: true,
      name: "",
      username: "",
      identifier: "",
      password: "",
      loading: false,
      errorMessage: "",
      email: ""
    };
  },
  methods: {
    async handleSubmit() {
      this.loading = true;
      this.errorMessage = "";

      let response;
      if (this.isLogin) {
        response = await loginUser(this.identifier, this.password);
      } else {
        response = await registerUser(this.name, this.username, this.identifier, this.password);
      }

      if (response.success) {
        if (this.isLogin) {
          this.$router.push("/order"); 
        } else {
          this.isLogin = true; 
        }
      } else {
        this.errorMessage = response.error;
      }

      this.loading = false;
    },
    toggleMode() {
      this.isLogin = !this.isLogin;
      this.errorMessage = "";
    }
  }
};
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: auto;
  padding: 20px;
}
.error {
  color: red;
}
.toggle {
  color: blue;
  cursor: pointer;
  margin-top: 10px;
}
</style>
