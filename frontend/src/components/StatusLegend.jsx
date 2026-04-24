function StatusLegend() {
  const item = (color, label) => (
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      <div
        style={{
          width: "16px",
          height: "16px",
          backgroundColor: color,
          borderRadius: "4px",
        }}
      />
      <span>{label}</span>
    </div>
  );

  return (
    <div
      style={{
        backgroundColor: "white",
        padding: "15px",
        borderRadius: "12px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
        display: "flex",
        justifyContent: "space-around",
      }}
    >
      {item("#4CAF50", "Success")}
      {item("#FFC107", "Running")}
      {item("#2196F3", "Queued")}
      {item("#F44336", "Failed")}
      {item("#9E9E9E", "Pending")}
    </div>
  );
}

export default StatusLegend;