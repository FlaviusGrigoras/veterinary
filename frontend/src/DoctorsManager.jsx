import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";

export default function DoctorsManager() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [form, setForm] = useState({
    user_id: "",
    specialization: "",
    bio: "",
  });

  const fetchData = async () => {
    try {
      const resUsers = await api.get("/users");
      setUsers(resUsers.data);
      const resDocs = await api.get("/doctors");
      setDoctors(resDocs.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/doctors", form);
      alert("Doctor profile saved!");
      setForm({ user_id: "", specialization: "", bio: "" });
      fetchData();
    } catch (err) {
      alert("Error: " + err.response?.data?.message);
    }
  };

  return (
    <div>
      <button onClick={() => navigate("/dashboard")}>Back</button>
      <h2>Add / Edit Doctor</h2>

      <form onSubmit={handleSubmit}>
        <label>Select User: </label>
        <select
          value={form.user_id}
          onChange={(e) => setForm({ ...form, user_id: e.target.value })}
          required
        >
          <option value="">-- Select --</option>
          {users.map((u) => (
            <option key={u.ID} value={u.ID}>
              {u.Name} ({u.Email})
            </option>
          ))}
        </select>
        <br />
        <br />
        <input
          placeholder="Specialization"
          value={form.specialization}
          onChange={(e) => setForm({ ...form, specialization: e.target.value })}
          required
        />
        <br />
        <textarea
          placeholder="Bio"
          value={form.bio}
          onChange={(e) => setForm({ ...form, bio: e.target.value })}
          required
        />
        <br />
        <button type="submit">Save</button>
      </form>

      <h3>Existing Doctors</h3>
      <ul>
        {doctors.map((d) => (
          <li key={d.doctor_id}>
            <strong>{d.name}</strong> - {d.specialization} ({d.bio})
          </li>
        ))}
      </ul>
    </div>
  );
}
