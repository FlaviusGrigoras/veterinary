import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";

export default function AppointmentsList() {
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const role = localStorage.getItem("role");
  const userId = localStorage.getItem("userId");

  const fetchAppointments = async () => {
    let query = "";

    if (role === "client") {
      query = `?client_id=${userId}`;
    } else if (role !== "admin") {
      try {
        const docRes = await api.get("/doctors");
        const myDoc = docRes.data.find((d) => d.user_id === userId);
        if (myDoc) query = `?doctor_id=${myDoc.doctor_id}`;
      } catch (e) {}
    }

    try {
      const res = await api.get(`/appointments${query}`);
      setAppointments(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, []);

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/appointment/${id}`, { status });
      fetchAppointments();
    } catch (err) {
      alert("Error updating status");
    }
  };

  return (
    <div>
      <button onClick={() => navigate("/dashboard")}>Back</button>
      <h2>Appointments List</h2>

      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Date</th>
            <th>Doctor</th>
            <th>Client</th>
            <th>Service</th>
            <th>Status</th>
            {(role === "admin" || role === "doctor") && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {appointments.map((app) => (
            <tr key={app.id}>
              <td>{new Date(app.start_time).toLocaleString()}</td>
              <td>{app.doctor_name}</td>
              <td>{app.client_name}</td>
              <td>{app.service_name}</td>
              <td>{app.status}</td>
              {(role === "admin" || role === "doctor") && (
                <td>
                  <button onClick={() => updateStatus(app.id, "completed")}>
                    Completed
                  </button>
                  <button onClick={() => updateStatus(app.id, "cancelled")}>
                    Cancelled
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
