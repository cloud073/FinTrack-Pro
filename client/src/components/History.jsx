import React, { useEffect, useState } from "react";
import axios from "axios";

function History({ token }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await axios.get("https://fintrack-pro-server.onrender.com/api/history", {
          headers: { Authorization: token },
        });
        setHistory(res.data.transactions); // updated key
      } catch (err) {
        console.error("History fetch failed:", err);
      }
    }

    fetchHistory();
  }, [token]);

  return (
    <div
      style={{
        marginTop: "2rem",
        padding: "1rem",
        background: "#ffffff",
        borderRadius: "10px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
      }}
    >
      <h3 style={{ marginBottom: "1rem" }}>🕘 Transaction History</h3>
      
      <div
        style={{
          maxHeight: "400px",
          overflowY: "auto",
          border: "1px solid #ddd",
          borderRadius: "8px",
          padding: "0.5rem 1rem",
          background: "#fafafa",
        }}
      >
        {history.length === 0 ? (
          <p style={{ fontStyle: "italic", color: "#888" }}>No transactions yet.</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {history.map((txn, i) => (
              <li
                key={i}
                style={{
                  padding: "0.5rem 0",
                  borderBottom: "1px solid #e0e0e0",
                  fontSize: "0.95rem",
                }}
              >
                <strong>{txn.date}</strong> — {txn.description} — ₹{txn.amount.toFixed(2)} —{" "}
                <span style={{ fontStyle: "italic", color: "#007bff" }}>{txn.category}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default History;
