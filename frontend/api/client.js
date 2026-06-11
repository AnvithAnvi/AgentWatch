import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export async function getRuns() {
  const response = await api.get("/runs/");
  return response.data;
}

export async function getRun(runId) {
  const response = await api.get(`/runs/${runId}`);
  return response.data;
}