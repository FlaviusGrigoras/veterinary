// axios ajuta la folosirea api-urilor
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://10.0.0.11:5001/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
