import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const username = localStorage.getItem("username");
    const role = localStorage.getItem("role");

    if (token) {
      setUser({ username, role });
    }
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    navigate("/");
  };

  if (!user) {
    return (
      <div style={{ textAlign: "center", marginTop: "50px" }}>
        <h1>Welcome to the clinic</h1>
        <p>Please login or register</p>
        <button
          onClick={() => navigate("/login")}
          style={{ fontSize: "20px", margin: "10px" }}
        >
          Login
        </button>
        <button
          onClick={() => navigate("/register")}
          style={{ fontSize: "20px", margin: "10px" }}
        >
          Register
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Hello, {user.username || "User"}!</h1>
      <p>Rol: {user.role}</p>
      <button onClick={handleLogout}>Logout</button>
      <hr />

      <h3>Home</h3>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          maxWidth: "300px",
        }}
      >
        <button onClick={() => navigate("/schedule")}>Schedule a Visit</button>
        <button onClick={() => navigate("/my-appointments")}>
          My Schedules
        </button>

        {user.role === "admin" && (
          <button
            onClick={() => navigate("/admin")}
            style={{
              backgroundColor: "red",
              color: "white",
              marginTop: "20px",
            }}
          >
            Admin Page
          </button>
        )}
      </div>
    </div>
  );
}
