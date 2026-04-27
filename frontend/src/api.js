const BASE_URL = "/api";

let authToken = localStorage.getItem("authToken");

export function setAuthToken(token) {
  authToken = token;
  localStorage.setItem("authToken", token);
}

export function clearAuthToken() {
  authToken = null;
  localStorage.removeItem("authToken");
}

async function apiRequest(url, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }
  const response = await fetch(`${BASE_URL}${url}`, { ...options, headers });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "API request failed");
  }

  return response.json();
}

export async function register(userData) {
  const result = await apiRequest("/register", { method: "POST", body: JSON.stringify(userData) });
  setAuthToken(result.access_token);
  return result;
}

export async function login(credentials) {
  const result = await apiRequest("/login", { method: "POST", body: JSON.stringify(credentials) });
  setAuthToken(result.access_token);
  return result;
}

export async function getProfile() {
  return apiRequest("/profile");
}

export async function sendChat(payload) {
  return apiRequest("/chat", { method: "POST", body: JSON.stringify(payload) });
}

export async function fetchTrends() {
  return apiRequest("/trends");
}

export async function checkHealth() {
  return apiRequest("/health");
}
