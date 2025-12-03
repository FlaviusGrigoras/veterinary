import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";

export default function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    first_name: "",
    last_name: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await api.post("/register", formData);
      alert("Account created successfully! Please login.");
      navigate("/login");
    } catch (err) {
      alert(
        "Registration error: " + (err.response?.data?.message || err.message)
      );
    }
  };

  return (
    <div>
      <h2>Register New Account</h2>
      <form onSubmit={handleRegister}>
        <div>
          <label>Email: </label>
          <input name="email" type="email" onChange={handleChange} required />
        </div>
        <div>
          <label>Username: </label>
          <input name="username" type="text" onChange={handleChange} required />
        </div>
        <div>
          <label>Password: </label>
          <input
            name="password"
            type="password"
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Last Name: </label>
          <input
            name="last_name"
            type="text"
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>First Name: </label>
          <input
            name="first_name"
            type="text"
            onChange={handleChange}
            required
          />
        </div>
        <br />
        <button type="submit">Create Account</button>
      </form>
      <br />
      <button onClick={() => navigate("/login")}>Back to Login</button>
    </div>
  );
}
