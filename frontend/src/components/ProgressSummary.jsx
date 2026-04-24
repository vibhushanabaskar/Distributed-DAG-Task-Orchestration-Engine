import { useEffect, useState } from "react";
import { getDagProgress } from "../services/api";

function ProgressSummary({ dagId, refreshTrigger }) {
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    fetchProgress();
    const interval = setInterval(fetchProgress, 2000);
    return () => clearInterval(interval);
  }, [dagId, refreshTrigger]);

  const fetchProgress = async () => {
    try {
      const res = await getDagProgress(dagId);
      setProgress(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (!progress) return null;

  return (
    <div style={{ display: "flex", gap: 20 }}>
      <Card title="Total" value={progress.total_tasks} />
      <Card title="Success" value={progress.SUCCESS} />
      <Card title="Running" value={progress.RUNNING} />
      <Card title="Failed" value={progress.FAILED} />
      <Card title="Completion" value={`${progress.completion_percentage}%`} />
    </div>
  );
}

const Card = ({ title, value }) => (
  <div
    style={{
      background: "white",
      padding: 20,
      borderRadius: 10,
      boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
      flex: 1,
      textAlign: "center",
    }}
  >
    <h4>{title}</h4>
    <p>{value}</p>
  </div>
);

export default ProgressSummary;