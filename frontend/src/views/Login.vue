<template>
  <div>
    <h1>Users Page</h1>
    <router-link to="/">Go to Home</router-link>

    <!-- Signup Form -->
    <h1>Sign Up</h1>
    <form @submit.prevent="signup">
      <label>Name:</label>
      <input type="text" v-model="name" required />

      <label>Email:</label>
      <input type="email" v-model="emailSignup" required />

      <label>Password:</label>
      <input type="password" v-model="passwordSignup" required />

      <button type="submit">Sign Up</button>
    </form>
    <p v-if="signupMessage" style="color: green;">{{ signupMessage }}</p>
    <p v-if="signupErrorMessage" style="color: red;">{{ signupErrorMessage }}</p>

    <!-- Login Form -->
    <h1>Login</h1>
    <form @submit.prevent="login">
      <label>Email:</label>
      <input type="email" v-model="emailLogin" required />

      <label>Password:</label>
      <input type="password" v-model="passwordLogin" required />

      <button type="submit">Login</button>
    </form>
    <p v-if="loginErrorMessage" style="color: red;">{{ loginErrorMessage }}</p>
  </div>
</template>

<script>
import axios from "axios";
import { useRouter } from "vue-router";

export default {
  data() {
    return {
      // Signup Fields
      name: "",
      emailSignup: "",
      passwordSignup: "",
      signupMessage: "",
      signupErrorMessage: "",

      // Login Fields
      emailLogin: "",
      passwordLogin: "",
      loginErrorMessage: "",
    };
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  methods: {

    async signup() {
      try {
        const response = await axios.post("http://localhost:5001/signup", {
          name: this.name,
          email: this.emailSignup,
          password: this.passwordSignup,
        });

        console.log("Signup successful:", response.data);
        this.signupMessage = "User created successfully!";
        this.signupErrorMessage = "";

      } catch (error) {
        console.error("Signup error:", error);
        this.signupErrorMessage = error.response?.data?.message || "Signup failed!";
      }
    },


    async login() {
      try {
        const response = await axios.post("http://localhost:5001/login", {
          email: this.emailLogin,
          password: this.passwordLogin,
        });

        console.log("Login successful:", response.data);

        // Store JWT Token & User Info in Local Storage
        localStorage.setItem("token", response.data.token);
        localStorage.setItem("user", JSON.stringify(response.data.user));

        alert("Login successful!");

        // Redirect to Order Page
        this.$router.push("/order");
      } catch (error) {
        console.error("Login error:", error);
        this.loginErrorMessage = error.response?.data?.message || "Login failed!";
      }
    },
  },
};
</script>
