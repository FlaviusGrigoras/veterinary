import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";

export default function ServicesManager() {
  const navigate = useNavigate();
  const [services, setServices] = useState([]);
  const [form, setForm] = useState({
    name: "",
    species: "",
    duration: "",
    price: "",
  });
  const [editingId, setEditingId] = useState(null);

  const fetchServices = async () => {
    try {
      const res = await api.get("/services");
      setServices(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchServices();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/services/${editingId}`, {
          price: parseFloat(form.price),
          duration: parseInt(form.duration),
        });
        alert("Service updated!");
      } else {
        await api.post("/services", form);
        alert("Service created!");
      }
      setForm({ name: "", species: "", duration: "", price: "" });
      setEditingId(null);
      fetchServices();
    } catch (err) {
      alert("Error: " + (err.response?.data?.message || err.message));
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Are you sure you want to delete this service?")) return;
    try {
      await api.delete(`/services/${id}`);
      fetchServices();
    } catch (err) {
      alert("Error deleting service: ", err);
    }
  };

  const startEdit = (service) => {
    setEditingId(service.id);
    setForm(service);
  };

  return (
    <div>
      <button onClick={() => navigate("/dashboard")}>Back</button>
      <h2>Services Management</h2>

      <form
        onSubmit={handleSubmit}
        style={{
          border: "1px solid black",
          padding: "10px",
          marginBottom: "20px",
        }}
      >
        <h3>{editingId ? "Edit (Price/Duration Only)" : "Add Service"}</h3>

        {!editingId && (
          <>
            <input
              placeholder="Service Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
            <br />
            <input
              placeholder="Species (e.g., Dogs)"
              value={form.species}
              onChange={(e) => setForm({ ...form, species: e.target.value })}
              required
            />
            <br />
          </>
        )}

        <input
          placeholder="Duration (minutes)"
          type="number"
          value={form.duration}
          onChange={(e) => setForm({ ...form, duration: e.target.value })}
          required
        />
        <br />
        <input
          placeholder="Price (RON)"
          type="number"
          value={form.price}
          onChange={(e) => setForm({ ...form, price: e.target.value })}
          required
        />
        <br />

        <button type="submit">{editingId ? "Save" : "Add"}</button>
        {editingId && (
          <button
            onClick={() => {
              setEditingId(null);
              setForm({ name: "", species: "", duration: "", price: "" });
            }}
          >
            Cancel
          </button>
        )}
      </form>

      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Name</th>
            <th>Species</th>
            <th>Duration</th>
            <th>Price</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {services.map((s) => (
            <tr key={s.id}>
              <td>{s.name}</td>
              <td>{s.species}</td>
              <td>{s.duration} min</td>
              <td>{s.price} RON</td>
              <td>
                <button onClick={() => startEdit(s)}>Edit</button>
                <button onClick={() => handleDelete(s.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
