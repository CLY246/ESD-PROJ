<template>
  <div>
    <h1>Users Page</h1>
    <router-link to="/">Go to Home</router-link>
    <!-- <p v-if="loading">Loading...</p>
    <ul v-if="!loading">
      <li v-for="user in users" :key="user.id">
        {{ user.name }} - {{ user.email }}
      </li>
    </ul> -->
    <h1>Sign Up</h1>
    <form @submit.prevent="signup">
      <label>Name:</label>
      <input type="text" v-model="name" required />

      <label>Email:</label>
      <input type="email" v-model="email" required />

      <label>Password:</label>
      <input type="password" v-model="password" required />

      <button type="submit">Sign Up</button>
    </form>

    <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
  </div>
  <div>
    <h1>Login</h1>
    <form @submit.prevent="login">
      <label>Email:</label>
      <input type="email" v-model="email" required />

      <label>Password:</label>
      <input type="password" v-model="password" required />

      <button type="submit">Login</button>
    </form>

    <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
  </div>
</template>
<!-- 
<script>
import axios from "axios";
var userurl = "http://localhost:5001/api/users";

export default {
  data() {
    return {
      users: [],
      loading: true,
    };
  },

  methods: {
    getAllusers() {
      const response = axios
        .get(userurl)
        .then((response) => {
          console.log(response.data);
          this.users = response.data;
        })
        .catch((error) => {
          console.error(error);
        })
        .finally(()=>{
          this.loading = false;
        });
    },
  },
  created() {
    this.getAllusers();
  },
};
</script> -->


<script>
import axios from "axios";

export default {
  data() {
    return {
      name: "",
      email: "",
      password: "",
      token: localStorage.getItem("token") || "",
      errorMessage: "",
    };
  },
  methods: {
    async signup() {
      try {
        const response = await axios.post("http://localhost:5001/signup", {
          name: this.name,  // Include name in request
          email: this.email,
          password: this.password,
        });

        console.log("Signup successful:", response.data);
        alert("User created successfully!");

      } catch (error) {
        console.error("Signup error:", error);
        this.errorMessage = error.response?.data?.message || "Signup failed!";
      }
    },
    async login() {
      try {
        const response = await axios.post("http://localhost:5001/login", {
          email: this.email,
          password: this.password,
        });

        console.log("Login successful:", response.data);
        
        // Save JWT token in localStorage
        localStorage.setItem("token", response.data.token);

        alert("Login successful!");

        // Redirect to dashboard/homepage
        this.$router.push("/");
      } catch (error) {
        console.error("Login error:", error);
        this.errorMessage = error.response?.data?.message || "Login failed!";
      }
    },
  },
};
</script>
