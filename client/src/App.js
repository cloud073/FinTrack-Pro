import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import UploadForm from "./components/UploadForm";
import SpendingChart from "./components/SpendingChart";

const API_BASE_URL = "https://fintrack-pro-server.onrender.com";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [authMode, setAuthMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", username: "" });
  const [showHistory, setShowHistory] = useState(false);
  const [historyData, setHistoryData] = useState([]);
  const [summaryData, setSummaryData] = useState([]);
  const [refresh, setRefresh] = useState(false);

  // 🔍 New filter states
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [limitFilter, setLimitFilter] = useState("All");

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const toggleMode = () => setAuthMode((prev) => (prev === "login" ? "register" : "login"));

  const handleAuth = async (e) => {
    e.preventDefault();
    const url =
      authMode === "login"
        ? `${API_BASE_URL}/api/login`
        : `${API_BASE_URL}/api/register`;
    const payload =
      authMode === "login"
        ? { username: form.username, password: form.password }
        : form;
    try {
      const res = await axios.post(url, payload);
      if (authMode === "login") {
        localStorage.setItem("token", res.data.token);
        setToken(res.data.token);
        alert("✅ Logged in!");
        fetchSummary(res.data.token);
      } else {
        alert("✅ Registered! Please log in.");
        setAuthMode("login");
      }
    } catch (err) {
      alert("❌ " + (err.response?.data?.error || "Something went wrong"));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setSummaryData([]);
  };

  const fetchSummary = async (authToken = token) => {
    if (!authToken) return;
    try {
      const res = await axios.get(`${API_BASE_URL}/api/summary`, {
        headers: { Authorization: authToken },
      });
      setSummaryData(res.data.summary || []);
    } catch (err) {
      console.error("❌ Failed to fetch summary", err);
    }
  };

  const fetchHistory = useCallback(async () => {
    try {
      const params = {};
      if (categoryFilter && categoryFilter !== "All") {
        params.category = categoryFilter;
      }
      if (limitFilter && limitFilter !== "All") {
        params.limit = limitFilter;
      }

      const res = await axios.get(`${API_BASE_URL}/api/history`, {
        headers: { Authorization: token },
        params: params,
      });

      setHistoryData(res.data.transactions || []);
      setShowHistory(true);

      // Also refresh summary
      const summary = await axios.get(`${API_BASE_URL}/api/summary`, {
        headers: { Authorization: token },
      });
      setSummaryData(summary.data.summary || []);
      setRefresh((r) => !r);
    } catch (err) {
      alert("❌ Failed to load history");
    }
  }, [token, categoryFilter, limitFilter]);

  useEffect(() => {
    if (token && showHistory) {
      fetchHistory();
    }
  }, [token, showHistory, fetchHistory]);

  const deleteTransaction = async (id) => {
    if (!window.confirm("Are you sure you want to delete this transaction?")) return;
    try {
      await axios.delete(`${API_BASE_URL}/api/delete-transaction/${id}`, {
        headers: { Authorization: token },
      });
      fetchHistory();
    } catch (err) {
      alert("❌ Failed to delete transaction");
    }
  };

  const deleteAllTransactions = async () => {
    if (!window.confirm("Are you sure you want to delete ALL your history?")) return;
    try {
      await axios.delete(`${API_BASE_URL}/api/delete-all-transactions`, {
        headers: { Authorization: token },
      });
      fetchHistory();
    } catch (err) {
      alert("❌ Failed to delete all history");
    }
  };

  // 🧠 Filtered data logic
  const filteredHistory = historyData
    .filter((txn) => categoryFilter === "All" || txn.category === categoryFilter)
    .slice(0, limitFilter === "All" ? historyData.length : parseInt(limitFilter));

  const uniqueCategories = [...new Set(historyData.map((txn) => txn.category))];

  useEffect(() => {
    if (token && showHistory) {
      fetchHistory();
    }
  }, [limitFilter, fetchHistory, showHistory, token]);

  return (
    <div style={{ fontFamily: "Arial, sans-serif" }}>
      {/* Header */}
      <div style={header}>
        <h1 style={{ margin: 0 }}>📊 FinTrack Pro</h1>
        {token && (
          <div>
            <button onClick={fetchHistory} title="View History" style={iconBtn}>
              📜
            </button>
            <button onClick={handleLogout} title="Logout" style={iconBtn}>
              🚪
            </button>
          </div>
        )}
      </div>

      {/* Auth */}
      {!token ? (
        <div style={card}>
          <h2 style={{ textAlign: "center" }}>
            {authMode === "login" ? "Login" : "Register"}
          </h2>
          <form onSubmit={handleAuth}>
            {authMode === "register" && (
              <>
                <input
                  name="username"
                  placeholder="Username"
                  style={input}
                  value={form.username}
                  onChange={handleChange}
                  required
                />
                <input
                  name="email"
                  placeholder="Email"
                  type="email"
                  style={input}
                  value={form.email}
                  onChange={handleChange}
                  required
                />
              </>
            )}
            {authMode === "login" && (
              <input
                name="username"
                placeholder="Username or Email"
                style={input}
                value={form.username}
                onChange={handleChange}
                required
              />
            )}
            <input
              name="password"
              type="password"
              placeholder="Password"
              style={input}
              value={form.password}
              onChange={handleChange}
              required
            />
            <button type="submit" style={button}>
              {authMode === "login" ? "Login" : "Register"}
            </button>
          </form>
          <p style={{ textAlign: "center", marginTop: "1rem" }}>
            {authMode === "login" ? "New user?" : "Already registered?"}{" "}
            <button onClick={toggleMode} style={linkBtn}>
              {authMode === "login" ? "Register" : "Login"}
            </button>
          </p>
        </div>
      ) : (
        <div style={{ maxWidth: "800px", margin: "0 auto", padding: "1rem" }}>
          <UploadForm
            token={token}
            onUploadComplete={() => {
              fetchSummary();
              setRefresh((r) => !r);
            }}
          />
          <SpendingChart
            token={token}
            refresh={refresh}
            summaryData={summaryData}
          />

          {/* Upload New File Button */}
          <div style={{ textAlign: "center", marginTop: "3rem" }}>
            <button
              onClick={() => {
                window.scrollTo(0, 0);
                setTimeout(() => window.location.reload(), 100);
              }}
              style={{
                padding: "0.8rem 1.5rem",
                background: "#6c757d",
                color: "white",
                border: "none",
                borderRadius: "6px",
                fontWeight: "bold",
                cursor: "pointer",
              }}
            >
              🔄 Upload New File
            </button>
          </div>

          {/* History Modal */}
          {showHistory && (
            <div style={modalOverlay}>
              <div style={modalContent}>
                <button
                  onClick={() => {
                    setShowHistory(false);
                    fetchSummary();
                    setRefresh((r) => !r);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                  style={modalClose}
                >
                  ❌
                </button>

                <h3>📜 Transaction History</h3>

                {/* Filters */}
                <div
                  style={{
                    display: "flex",
                    gap: "1rem",
                    marginBottom: "1rem",
                  }}
                >
                  <div>
                    <label>Category: </label>
                    <select
                      value={categoryFilter}
                      onChange={(e) => setCategoryFilter(e.target.value)}
                    >
                      <option value="All">All</option>
                      {uniqueCategories.map((cat, idx) => (
                        <option key={idx} value={cat}>
                          {cat}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label>Limit: </label>
                    <select
                      value={limitFilter}
                      onChange={(e) => setLimitFilter(e.target.value)}
                    >
                      <option value="All">Max(1000)</option>
                      <option value="10">First 10</option>
                      <option value="50">First 50</option>
                      <option value="100">First 100</option>
                    </select>
                  </div>
                </div>

                {filteredHistory.length > 0 ? (
                  <>
                    <ul
                      style={{
                        maxHeight: "300px",
                        overflowY: "auto",
                        paddingLeft: "1rem",
                      }}
                    >
                      {filteredHistory.map((txn) => (
                        <li key={txn.id} style={txnItem}>
                          <span>
                            <strong>{txn.date}</strong> — {txn.description} — ₹
                            {txn.amount} —{" "}
                            <i style={{ color: "#555" }}>{txn.category}</i>
                          </span>
                          <button
                            onClick={() => deleteTransaction(txn.id)}
                            style={deleteBtn}
                          >
                            🗑️
                          </button>
                        </li>
                      ))}
                    </ul>
                    <div
                      style={{ textAlign: "center", marginTop: "1rem" }}
                    >
                      <button
                        onClick={deleteAllTransactions}
                        style={deleteAllBtn}
                      >
                        ❌ Delete All History
                      </button>
                    </div>
                  </>
                ) : (
                  <p>No history available.</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Styles
const header = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "1rem 2rem",
  backgroundColor: "#f0f0f0",
  borderBottom: "1px solid #ccc",
};
const card = {
  maxWidth: "400px",
  margin: "2rem auto",
  padding: "2rem",
  borderRadius: "12px",
  background: "#f8f8f8",
  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
};
const input = {
  width: "100%",
  padding: "0.6rem",
  margin: "0.5rem 0",
  borderRadius: "6px",
  border: "1px solid #ccc",
};
const button = {
  width: "100%",
  padding: "0.8rem",
  marginTop: "1rem",
  background: "#007bff",
  color: "white",
  border: "none",
  borderRadius: "6px",
  fontWeight: "bold",
  cursor: "pointer",
};
const linkBtn = {
  background: "none",
  border: "none",
  color: "#007bff",
  cursor: "pointer",
  textDecoration: "underline",
};
const iconBtn = {
  background: "none",
  border: "none",
  fontSize: "1.2rem",
  cursor: "pointer",
  marginLeft: "1rem",
};
const modalOverlay = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100vw",
  height: "100vh",
  background: "rgba(0,0,0,0.4)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
};
const modalContent = {
  background: "#fff",
  padding: "2rem",
  borderRadius: "12px",
  width: "95%",
  maxWidth: "900px",
  maxHeight: "90vh",
  overflowY: "auto",
  position: "relative",
  boxShadow: "0 0 15px rgba(0, 0, 0, 0.2)",
};
const modalClose = {
  position: "absolute",
  top: "1rem",
  right: "1rem",
  background: "transparent",
  border: "none",
  fontSize: "1.2rem",
  cursor: "pointer",
};
const txnItem = {
  marginBottom: "0.5rem",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};
const deleteBtn = {
  background: "none",
  border: "none",
  color: "red",
  fontSize: "1rem",
  cursor: "pointer",
};
const deleteAllBtn = {
  background: "red",
  color: "white",
  padding: "0.6rem 1.2rem",
  border: "none",
  borderRadius: "6px",
  fontWeight: "bold",
  cursor: "pointer",
};

export default App;
