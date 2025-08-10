import React, { useState } from "react";
import axios from "axios";

function UploadForm({ token, onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("❗ Please select a CSV file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setUploading(true);

    try {
      const res = await axios.post("http://localhost:5000/api/upload-csv", formData, {
        headers: {
          Authorization: token,
        },
      });

      setTransactions(res.data.transactions || []);
      setFile(null); // Reset file input
      alert("✅ CSV uploaded successfully!");

      if (onUploadComplete) onUploadComplete(); // refresh charts

    } catch (err) {
      console.error("Upload error:", err);
      alert("❌ Upload failed: " + (err.response?.data?.error || "Unknown error"));
    } finally {
      setUploading(false);
    }
  };

  const styles = {
    card: {
      marginTop: "2rem",
      padding: "1.5rem",
      borderRadius: "12px",
      background: "#f9f9f9",
      boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
    },
    fileInput: {
      padding: "0.6rem",
      fontSize: "1rem",
      marginBottom: "1rem",
      display: "block",
    },
    uploadButton: {
      padding: "0.8rem 1.5rem",
      background: uploading ? "#6c757d" : "#007bff",
      color: "white",
      border: "none",
      borderRadius: "6px",
      cursor: uploading ? "not-allowed" : "pointer",
      fontWeight: "bold",
    },
    listWrapper: {
      marginTop: "2rem",
      maxHeight: "250px",
      overflowY: "auto",
      border: "1px solid #ccc",
      borderRadius: "8px",
      padding: "1rem",
      backgroundColor: "#fff",
    },
    listItem: {
      marginBottom: "0.5rem",
      fontSize: "1rem",
      borderBottom: "1px dashed #ccc",
      paddingBottom: "0.3rem",
    },
  };

  return (
    <div style={styles.card}>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
          style={styles.fileInput}
          disabled={uploading}
        />
        <button type="submit" style={styles.uploadButton} disabled={uploading}>
          {uploading ? "⏳ Uploading..." : "📤 Upload CSV"}
        </button>
      </form>

      {transactions.length > 0 && (
        <div style={styles.listWrapper}>
          <h3>📄 Uploaded Transactions:</h3>
          <ul>
            {transactions.map((txn, idx) => (
              <li key={idx} style={styles.listItem}>
                <strong>{txn.date}</strong> — {txn.description} — ₹{txn.amount} —{" "}
                <span style={{ color: "#555", fontStyle: "italic" }}>{txn.category}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default UploadForm;
