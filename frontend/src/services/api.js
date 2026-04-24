import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

export const createDag = (payload) =>
  API.post("/dags/", payload);

export const getDagDetails = (dagId) =>
  API.get(`/dags/${dagId}`);

export const getDagProgress = (dagId) =>
  API.get(`/dags/${dagId}/progress`);

export const getTaskLogs = (taskId) =>
  API.get(`/tasks/${taskId}/logs`);

export const checkBackendHealth = () =>
  API.get("/health");

export const getDagList = () =>
  API.get("/dags");