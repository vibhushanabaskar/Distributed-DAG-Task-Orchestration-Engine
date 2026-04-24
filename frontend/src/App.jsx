import { useEffect, useState } from "react";
import DagView from "./components/DagView";
import ProgressSummary from "./components/ProgressSummary";
import StatusLegend from "./components/StatusLegend";
import {
  createDag,
  checkBackendHealth,
  getDagList,
} from "./services/api";

function App() {
  const [dagId, setDagId] = useState(null);
  const [createdDags, setCreatedDags] = useState([]);
  const [backendStatus, setBackendStatus] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [loading, setLoading] = useState(false);

  // NEW: Workflow Builder state
  const [showBuilder, setShowBuilder] = useState(false);
  const [tasks, setTasks] = useState([
  { id: "", command: "", file_path: "", dependencies: [] }
]);

  useEffect(() => {
    checkHealth();
    fetchDags();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      await checkBackendHealth();
      setBackendStatus(true);
    } catch {
      setBackendStatus(false);
    }
  };

  const fetchDags = async (newDagId = null) => {
    try {
      const res = await getDagList();
      const dagIds = res.data;

      setCreatedDags(dagIds);

      if (newDagId) {
        setDagId(newDagId);
      } else if (!dagId && dagIds.length > 0) {
        setDagId(dagIds[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };  

  // Add new task row
  const addTask = () => {
  setTasks([...tasks, { id: "", command: "", file_path: "", dependencies: [] }]);
};


  const updateTask = (index, field, value) => {
  const updated = [...tasks];
  updated[index][field] = value;
  setTasks(updated);
  };


  const handleFileUpload = async (event, index) => {
    const file = event.target.files[0];

    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      const updated = [...tasks];
      updated[index].file_path = data.file_path;

      setTasks(updated);

    } catch (error) {
      console.error("File upload failed:", error);
    }
  };

  const handleCreateDag = async () => {
  try {
    setLoading(true);

    const validTasks = tasks.filter(
    task =>
    task.id.trim() !== "" &&
    (task.command.trim() !== "" || task.file_path !== "")
    );

    if (validTasks.length === 0) {
      alert("Add at least one valid task.");
      return;
    }

    // Check duplicates
    const ids = validTasks.map(t => t.id);
    const uniqueIds = new Set(ids);
    if (ids.length !== uniqueIds.size) {
      alert("Duplicate Task IDs detected.");
      return;
    }

    // Validate dependencies
    for (let task of validTasks) {
      for (let dep of task.dependencies) {
        if (!ids.includes(dep)) {
          alert(`Invalid dependency "${dep}" in task "${task.id}"`);
          return;
        }
      }
    }

    const uniqueId = Math.random().toString(36).substring(2, 8);
    const runId = `test_dag_${uniqueId}`;


    const modifiedTasks = validTasks.map(task => ({
      id: `${task.id}_${runId}`,
      command: task.command,
      file_path: task.file_path,
      dependencies: task.dependencies.map(
        dep => `${dep}_${runId}`
      )
    }));

    const payload = {
      dag_id: runId,
      tasks: modifiedTasks
    };

    await createDag(payload);

    setShowBuilder(false);
    setTasks([{ id: "", command: "", file_path: "", dependencies: [] }]);

    fetchDags(runId);
    // setDagId(runId);

  } catch (err) {
    console.error("CREATE ERROR:", err.response?.data || err);
    alert("Backend rejected the task work flow beacuse it has cycles. Check console. Try again");
  } finally {
    setLoading(false);
  }
};

  

  return (
    <div style={{ padding: "40px" }}>
      <h1>DAG Orchestrator Dashboard</h1>

      <div style={{ marginBottom: 20 }}>
        Backend:
        <span
          style={{
            marginLeft: 10,
            color: backendStatus ? "green" : "red",
            fontWeight: 600,
          }}
        >
          {backendStatus ? "Connected" : "Disconnected"}
        </span>
      </div>

      {/* Controls */}
      <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
        <button onClick={() => setShowBuilder(true)}>
          Create DAG
        </button>

        {createdDags.length > 0 && (
          <select
            value={dagId || ""}
            onChange={(e) => setDagId(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: "6px",
              minWidth: "250px",
            }}
          >
            {createdDags.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        )}

        
      </div>

      {/* WORKFLOW BUILDER MODAL */}
      {showBuilder && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            background: "rgba(0,0,0,0.4)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 1000
          }}
        >
          <div
            style={{
              background: "white",
              padding: "30px",
              borderRadius: "12px",
              width: "600px",
              maxHeight: "80vh",      // limit height
              overflowY: "auto"       // enable vertical scroll
            }}
          >
            <h2>Create Workflow</h2>

            {tasks.map((task, index) => (
              <div key={index} style={{ marginBottom: 15 }}>
                <input
                  placeholder="Task ID"
                  value={task.id}
                  onChange={(e) =>
                    updateTask(index, "id", e.target.value)
                  }
                  style={{ marginRight: 10 }}
                />

                <input
                  placeholder="Command"
                  value={task.command}
                  onChange={(e) =>
                    updateTask(index, "command", e.target.value)
                  }
                  style={{ marginRight: 10, width: 250 }}
                />

                <input
                type="file"
                accept=".py"
                onChange={(e) =>
                  handleFileUpload(e, index)
                }
                style={{ marginRight: 10 }}
              />

              <div style={{ marginTop: 8 }}>
                <div style={{ fontSize: 12, marginBottom: 4 }}>
                  Dependencies:
                </div>

                <div
                style={{
                  maxHeight: "120px",      // height limit
                  overflowY: "auto",       // enable scroll
                  border: "1px solid #ddd",
                  borderRadius: "6px",
                  padding: "8px",
                  background: "#fafafa"
                }}
                >

                {tasks
                  .filter((_, i) => i !== index)
                  .map((t, i) => (
                    t.id && (
                      <label
                        key={i}
                        style={{
                          display: "block",
                          fontSize: 14,
                          cursor: "pointer"
                        }}
                      >
                        <input
                          type="checkbox"
                          value={t.id}
                          checked={task.dependencies.includes(t.id)}
                          onChange={(e) => {
                            let updatedDeps = [...task.dependencies];

                            if (e.target.checked) {
                              updatedDeps.push(t.id);
                            } else {
                              updatedDeps = updatedDeps.filter(dep => dep !== t.id);
                            }

                            updateTask(index, "dependencies", updatedDeps);
                          }}
                          style={{ marginRight: 6 }}
                        />
                        {t.id}
                      </label>
                    )
                  ))}
                </div>  
              </div>                
              </div>
            ))}

            <div style={{ marginTop: 15 }}>
              <button onClick={addTask}>
                Add Task
              </button>

              <button
                onClick={handleCreateDag}
                style={{ marginLeft: 10 }}
              >
                Submit DAG
              </button>

              <button
                onClick={() => setShowBuilder(false)}
                style={{ marginLeft: 10 }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dashboard */}
      {dagId && (
        <>
          <ProgressSummary
            dagId={dagId}
            refreshTrigger={refreshTrigger}
          />
          <StatusLegend />
          <div style={{ height: "70vh", marginTop: 20 }}>
            <DagView
              dagId={dagId}
              refreshTrigger={refreshTrigger}
            />
          </div>
        </>
      )}
    </div>
  );
}

export default App;