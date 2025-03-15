import axios from "axios";

const API_URL = "http://localhost:5001"; // Adjust this if deployed

// ✅ Login API Request (Supports Both Email & Username)
export async function loginUser(identifier, password) {
    try {
        const response = await axios.post(`${API_URL}/login`, {
            identifier, // ✅ Can be email or username
            password
        });

        if (response.data.access_token) {
            localStorage.setItem("token", response.data.access_token);
        }

        return { success: true, data: response.data };

    } catch (error) {
        console.error("❌ Login error:", error.response?.data?.error || error.message);
        return { success: false, error: error.response?.data?.error || "Login failed" };
    }
}

// ✅ Register API Request (Now Includes `name`)
export async function registerUser(name, username, email, password) {
    try {
        const response = await axios.post(`${API_URL}/register`, {
            name,
            username,
            email,
            password
        });

        return { success: true, data: response.data };

    } catch (error) {
        console.error("❌ Registration error:", error.response?.data?.error || error.message);
        return { success: false, error: error.response?.data?.error || "Registration failed" };
    }
}
