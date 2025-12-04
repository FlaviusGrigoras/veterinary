import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";

export default function UsersManager() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);

  const fetchUsers = async () => {
    try {
      const res = await api.get("/users");
      setUsers(res.data);
    } catch (err) {
      console.error(err);
      alert("Could not load users");
    }
  };

  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    if (
      !window.confirm(
        `Are you sure you want to change this user's role to ${newRole}?`
      )
    ) {
      fetchUsers();
      return;
    }
    try {
      await api.put(`/user/${userId}`, { role: newRole });
      alert("Role modified succesfully!");
      fetchUsers();
    } catch (err) {
      alert("Error: " + (err.response?.data?.message || err.message));
      fetchUsers();
    }
  };

  return (
    <div>
      <button onClick={() => navigate("/dashboard")}>Back to Dashboard</button>
      <h2>User Management</h2>

      <table
        border="1"
        cellPadding="10"
        style={{ width: "100%", borderCollapse: "collapse" }}
      >
        <thead>
          <tr style={{ backgroundColor: "#f2f2f2" }}>
            <th>Name</th>
            <th>Email</th>
            <th>Current Role</th>
            <th>Actions (Change Role)</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.ID}>
              <td>{u.Name}</td>
              <td>{u.Email}</td>
              <td>
                <strong>{u.Role}</strong>
              </td>
              <td>
                <select
                  value={u.Role}
                  onChange={(e) => handleRoleChange(u.ID, e.target.value)}
                >
                  <option value="client">Client</option>
                  <option value="doctor">Doctor</option>
                  <option value="admin">Admin</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
