import axios from "axios";

// Environment variable for API URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Interceptor for handling errors globally (e.g., specific to TraceData error codes)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Basic error logging - can be enhanced with monitoring service later
    console.error("API Call Failed:", error.response?.data || error.message);
    return Promise.reject(error);
  },
);
