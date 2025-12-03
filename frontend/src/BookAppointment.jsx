import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";

export default function BookAppointment() {
  const navigate = useNavigate();
  const [services, setServices] = useState([]);
  const [doctors, setDoctors] = useState([]);

  const [selectedService, setSelectedService] = useState("");
  const [selectedDoctor, setSelectedDoctor] = useState("");
  const [dateTime, setDateTime] = useState("");

  useEffect(() => {
    const loadData = async () => {
      const s = await api.get("/services");
      setServices(s.data);
      const d = await api.get("/doctors");
      setDoctors(d.data);
    };
    loadData();
  }, []);

  const handleBooking = async (e) => {
    e.preventDefault();
    const clientId = localStorage.getItem("userId");
    const formattedDate = new Date(dateTime).toISOString();

    try {
      await api.post("/appointments", {
        client_id: clientId,
        doctor_id: selectedDoctor,
        service_id: selectedService,
        start_time: formattedDate,
        status: "scheduled",
      });
      alert("Booking successful!");
      navigate("/my-appointments");
    } catch (err) {
      alert("Error: " + (err.response?.data?.message || err.message));
      if (err.response?.data?.conflict_with)
        alert("Time slot occupied: " + err.response.data.conflict_with);
    }
  };

  return (
    <div>
      <button onClick={() => navigate("/dashboard")}>Back</button>
      <h2>Book an Appointment</h2>
      <form onSubmit={handleBooking}>
        <label>Service: </label>
        <select onChange={(e) => setSelectedService(e.target.value)} required>
          <option value="">-- Select --</option>
          {services.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name} ({s.price} RON)
            </option>
          ))}
        </select>
        <br />
        <br />

        <label>Doctor: </label>
        <select onChange={(e) => setSelectedDoctor(e.target.value)} required>
          <option value="">-- Select --</option>
          {doctors.map((d) => (
            <option key={d.doctor_id} value={d.doctor_id}>
              {d.name} ({d.specialization})
            </option>
          ))}
        </select>
        <br />
        <br />

        <label>Date and Time: </label>
        <input
          type="datetime-local"
          onChange={(e) => setDateTime(e.target.value)}
          required
        />
        <br />
        <br />

        <button type="submit">Book Now</button>
      </form>
    </div>
  );
}
