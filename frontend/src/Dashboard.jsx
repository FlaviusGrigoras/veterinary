import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();
  const [role, setRole] = useState("");

  useEffect(() => {
    const storedRole = localStorage.getItem("role");
    setRole(storedRole);
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <div>
      <h1>Veterinary Dashboard</h1>
      <p>
        Logged in as: <strong>{role}</strong>
      </p>

      <hr />
      <h3>Menu</h3>
      <ul>
        <li>
          <button onClick={() => navigate("/my-appointments")}>
            View My Appointments
          </button>
        </li>

        {role === "client" && (
          <li>
            <button onClick={() => navigate("/book-appointment")}>
              Book New Appointment
            </button>
          </li>
        )}

        {role === "admin" && (
          <>
            <li>
              <button onClick={() => navigate("/services")}>
                Manage Services
              </button>
            </li>
            <li>
              <button onClick={() => navigate("/doctors")}>
                Manage Doctors
              </button>
            </li>
          </>
        )}
      </ul>

      <hr />
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
