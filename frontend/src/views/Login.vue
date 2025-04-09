<template>
  <div class="auth-background">
    <div class="auth-wrapper">
      <div class="auth-card">
        <h2 class="auth-title">{{ isLogin ? "Login" : "Sign Up" }}</h2>

        <form class="auth-form" @submit.prevent="handleSubmit">
          <input
            v-if="!isLogin"
            type="text"
            v-model="name"
            placeholder="Name"
            required
          />
          <input
            v-if="!isLogin"
            type="text"
            v-model="username"
            placeholder="Username"
            required
          />
          <input
            :type="isLogin ? 'text' : 'email'"
            v-model="identifier"
            :placeholder="isLogin ? 'Username / Email' : 'Email'"
            required
          />
          <input
            type="password"
            v-model="password"
            placeholder="Password"
            required
          />

          <div v-if="isLogin" class="auth-options">
            <label>
              <input type="checkbox" v-model="rememberMe" />
              Remember Me
            </label>
            <div class="links">
              <a href="#">Forgot Password?</a>
            </div>
          </div>

          <button type="submit" :disabled="loading">
            {{ isLogin ? "Login" : "Sign Up" }}
          </button>

          <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
        </form>

        <p class="toggle" @click="toggleMode">
          {{
            isLogin
              ? "Don't have an account? Sign Up"
              : "Already have an account? Login"
          }}
        </p>
      </div>
    </div>
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
      rememberMe: false,
      loading: false,
      errorMessage: "",
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
        response = await registerUser(
          this.name,
          this.username,
          this.identifier,
          this.password
        );
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
    },
  },
};
</script>

<style scoped>
.auth-background {
  height: 100vh;
  width: 100vw;
  background: radial-gradient(
      circle at center,
      rgba(144, 238, 144, 0.15),
      rgba(255, 255, 255, 0.9)
    ),
    linear-gradient(to bottom right, #e6f9e6, #f0fff0);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 20px;
}

.brand {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #fff;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  text-transform: uppercase;
}

.auth-wrapper {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 40px;
  border-radius: 20px;
  background-color: rgba(255, 255, 255, 0.75);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 420px;
  text-align: center;
}

.auth-title {
  font-size: 20px;
  margin-bottom: 24px;
  color: #333;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.auth-form input {
  padding: 10px 14px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 14px;
  background: white;
}

.auth-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #666;
}

.auth-options a {
  color: #097d4c;
  margin-left: 10px;
  text-decoration: none;
}

.auth-form button {
  margin-top: 14px;
  padding: 10px;
  background-color: #097d4c;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  font-size: 15px;
  cursor: pointer;
}

.auth-form button:hover {
  background-color: #097d4c;
}

.error-msg {
  margin-top: 10px;
  color: #e74c3c;
  font-size: 14px;
}

.toggle {
  margin-top: 16px;
  font-size: 13px;
  color: #097d4c;
  cursor: pointer;
}
</style>
