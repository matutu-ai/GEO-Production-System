const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_BASE ||
  "";
const TOKEN_KEY = "geo_token";
const USER_KEY = "geo_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user || {}));
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || "null") || {};
  } catch {
    return {};
  }
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `请求失败：${response.status}`);
  }
  return response.json();
}

export const api = {
  health: () => request("/api/health"),
  login: (username, password) =>
    request("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }),
  me: () => request("/api/users/me"),
  projects: () => request("/api/projects"),
  project: (taskId) => request(`/api/projects/${taskId}`),
  analyze: (formData) =>
    request("/api/analyze", {
      method: "POST",
      body: formData,
    }),
  createProject: (formData) =>
    request("/api/projects/create", {
      method: "POST",
      body: formData,
    }),
  rerun: (taskId) =>
    request(`/api/projects/${taskId}/rerun`, {
      method: "POST",
    }),
  deleteProject: (taskId) =>
    request(`/api/projects/${taskId}`, {
      method: "DELETE",
    }),
  downloadUrl: (taskId, filename) =>
    `${API_BASE}/api/projects/${taskId}/download/${encodeURIComponent(filename)}?token=${encodeURIComponent(getToken())}`,
};
