import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/login", { email, password });

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("userId", res.data.id);
      localStorage.setItem("role", res.data.role);
      alert("Login successfull!");
      navigate("/dashboard");
    } catch (err) {
      alert("Error: " + (err.response?.data?.message || err.message));
    }
  };

  return (
    <div>
      <form onSubmit={handleLogin}>
        <input
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <br />
        <input
          type="password"
          placeholder="Parola"
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <br />
        <button type="submit">Login</button>
      </form>
      <button onClick={() => navigate("/register")}>Register</button>
    </div>
  );
}
