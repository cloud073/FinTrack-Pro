import React, { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
} from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels";
import { Bar, Pie, Line, Doughnut } from "react-chartjs-2";

ChartJS.register(
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
  ChartDataLabels
);

function SpendingChart({ token, refresh, summaryData }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    if (summaryData && summaryData.length > 0) {
      setData(summaryData);
    } else {
      setData([]);
    }
  }, [summaryData, refresh]);

  const categoryLabels = data.map((item) => item.category);
  const categoryAmounts = data.map((item) => item.total);
  const totalSpent = categoryAmounts.reduce((sum, val) => sum + val, 0);

  const pieColors = [
    "#f94144", "#f3722c", "#f9844a", "#f9c74f",
    "#90be6d", "#43aa8b", "#577590", "#277da1",
    "#8e44ad", "#2ecc71"
  ];

  // 📊 Bar Chart
  const barData = {
    labels: categoryLabels,
    datasets: [
      {
        label: "Total Spent (₹)",
        data: categoryAmounts,
        backgroundColor: "#20c9a6",
        borderRadius: 6,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: "top" },
      title: {
        display: true,
        text: "Spending by Category (Bar Chart)",
        font: { size: 18 },
        padding: { top: 10, bottom: 20 },
      },
      datalabels: {
        anchor: "end",
        align: "top",
        formatter: (value) => `₹${value}`,
        font: { weight: "bold", size: 12 },
        color: "#111",
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Amount in ₹",
          font: { size: 14 },
        },
      },
      x: {
        title: {
          display: true,
          text: "Categories",
          font: { size: 14 },
        },
        ticks: {
          autoSkip: false,
          maxRotation: 45,
          minRotation: 30,
        },
      },
    },
  };

  // 🥧 Pie Chart
  const pieData = {
    labels: categoryLabels,
    datasets: [
      {
        data: categoryAmounts,
        backgroundColor: pieColors.slice(0, categoryLabels.length),
      },
    ],
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right",
        labels: { font: { size: 13 } },
      },
      title: {
        display: true,
        text: "Spending Distribution (Pie Chart)",
        font: { size: 18 },
        padding: { top: 10, bottom: 10 },
      },
      datalabels: {
        formatter: (value) => {
          const percentage = ((value / totalSpent) * 100).toFixed(1);
          return `${percentage}%`;
        },
        color: "#fff",
        font: { size: 13, weight: "bold" },
      },
    },
  };

  // 📈 Line Chart
  const lineData = {
    labels: categoryLabels,
    datasets: [
      {
        label: "Cumulative Spend (₹)",
        data: categoryAmounts.reduce((acc, val, i) => {
          acc.push(val + (acc[i - 1] || 0));
          return acc;
        }, []),
        fill: true,
        borderColor: "#007bff",
        backgroundColor: "rgba(0,123,255,0.1)",
        tension: 0.3,
        pointBackgroundColor: "#007bff",
      },
    ],
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "top" },
      title: {
        display: true,
        text: "Cumulative Spending Trend (Line Chart)",
        font: { size: 18 },
        padding: { top: 10, bottom: 20 },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Cumulative Amount (₹)",
          font: { size: 14 },
        },
      },
    },
  };

  // 🍩 Doughnut Chart
  const doughnutData = {
    labels: categoryLabels,
    datasets: [
      {
        data: categoryAmounts,
        backgroundColor: pieColors.slice(0, categoryLabels.length),
        borderWidth: 1,
      },
    ],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom",
        labels: { font: { size: 13 } },
      },
      title: {
        display: true,
        text: "Spending Overview (Doughnut Chart)",
        font: { size: 18 },
        padding: { top: 10, bottom: 10 },
      },
    },
  };

  return (
    <div style={{ marginTop: "2rem" }}>
      {/* Chart Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
          gap: "2rem",
          justifyContent: "center",
        }}
      >
        <ChartBox><Bar data={barData} options={barOptions} /></ChartBox>
        <ChartBox><Pie data={pieData} options={pieOptions} /></ChartBox>
        <ChartBox><Line data={lineData} options={lineOptions} /></ChartBox>
        <ChartBox><Doughnut data={doughnutData} options={doughnutOptions} /></ChartBox>
      </div>

      {/* Summary Table */}
      <div
        style={{
          marginTop: "3rem",
          background: "#fff",
          borderRadius: "12px",
          padding: "1.5rem",
          boxShadow: "0 0 10px rgba(0,0,0,0.05)",
          overflowX: "auto",
        }}
      >
        <h3 style={{ marginBottom: "1rem", color: "#333" }}>📋 Summary Table</h3>
        {data.length > 0 ? (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f2f2f2" }}>
                <th style={cellStyle}>Category</th>
                <th style={cellStyle}>Amount (₹)</th>
                <th style={cellStyle}>% of Total</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, idx) => (
                <tr key={idx} style={{ background: idx % 2 ? "#fcfcfc" : "#fff" }}>
                  <td style={cellStyle}>{item.category}</td>
                  <td style={cellStyle}>{item.total}</td>
                  <td style={cellStyle}>
                    {((item.total / totalSpent) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
              <tr style={{ fontWeight: "bold", background: "#e9ecef" }}>
                <td style={cellStyle}>Total</td>
                <td style={cellStyle}>{totalSpent}</td>
                <td style={cellStyle}>100%</td>
              </tr>
            </tbody>
          </table>
        ) : (
          <p>No data available.</p>
        )}
      </div>
    </div>
  );
}

// 📦 Chart Container Box
const ChartBox = ({ children }) => (
  <div
    style={{
      background: "#ffffff",
      padding: "1.5rem",
      borderRadius: "12px",
      minWidth: "300px",
      height: "450px",
      transition: "transform 0.2s",
      boxShadow: "0 4px 8px rgba(0,0,0,0.06)",
    }}
    onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.02)")}
    onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
  >
    {children}
  </div>
);

// 📋 Table Cell Style
const cellStyle = {
  border: "1px solid #ddd",
  padding: "0.75rem",
  textAlign: "center",
};

export default SpendingChart;
