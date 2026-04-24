import { useEffect, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
} from "reactflow";
import "reactflow/dist/style.css";
import {
  getDagDetails,
  getTaskLogs,
} from "../services/api";

const getColor = (status) => {
  switch (status) {
    case "SUCCESS":
      return "#4CAF50";
    case "RUNNING":
      return "#FFC107";
    case "FAILED":
      return "#F44336";
    case "QUEUED":
      return "#2196F3";
    default:
      return "#9E9E9E";
  }
};

function DagView({ dagId, refreshTrigger }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [logs, setLogs] = useState("");
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchDag();
    const interval = setInterval(fetchDag, 1000);
    return () => clearInterval(interval);
  }, [dagId, refreshTrigger]);

  const fetchDag = async () => {
    try {
      const response = await getDagDetails(dagId);
      const tasks = response.data.tasks;

      const newNodes = tasks.map((task, index) => ({
        id: task.id,
        data: { label: task.id },
        position: { x: 250 * index, y: 150 },
        style: {
          background: getColor(task.status),
          color: "white",
          padding: 10,
          borderRadius: 8,
        },
      }));

      const newEdges = tasks.flatMap((task) =>
        task.dependencies.map((dep) => ({
          id: `${dep}-${task.id}`,
          source: dep,
          target: task.id,
        }))
      );

      setNodes(newNodes);
      setEdges(newEdges);
    } catch (error) {
      console.error("Error fetching DAG:", error);
    }
  };

  const onNodeClick = async (_, node) => {
    try {
      const res = await getTaskLogs(node.id);
      setLogs(res.data.logs);
      setShowModal(true);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        onNodeClick={onNodeClick}
        style={{ width: "100%", height: "100%" }}
      >
        <Background />
        <Controls />
      </ReactFlow>

      {showModal && (
        <div style={modalStyle}>
          <div style={modalContent}>
            <h3>Task Logs</h3>
            <pre>{logs}</pre>
            <button onClick={() => setShowModal(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
}

const modalStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  background: "rgba(0,0,0,0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
};

const modalContent = {
  background: "white",
  padding: 20,
  width: "600px",
  maxHeight: "80vh",
  overflowY: "auto",
  borderRadius: 10,
};

export default DagView;