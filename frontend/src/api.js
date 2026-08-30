const API_BASE =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_BASE ||
  "";
const API_PREFIX = API_BASE ? "" : "/api";
const TOKEN_KEY = "geo_token";
const USER_KEY = "geo_user";
export const AUTH_EXPIRED_EVENT = "geo-auth-expired";

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
    if (response.status === 401) {
      clearAuth();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
      }
    }
    throw new Error(data.detail || `请求失败：${response.status}`);
  }
  return response.json();
}

export const api = {
  health: () => request(`${API_PREFIX}/health`),
  login: (username, password) =>
    request(`${API_PREFIX}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }),
  me: () => request(`${API_PREFIX}/users/me`),
  projects: () => request(`${API_PREFIX}/projects`),
  project: (taskId) => request(`${API_PREFIX}/tasks/${taskId}`),
  analyze: (formData) =>
    request(`${API_PREFIX}/analyze`, {
      method: "POST",
      body: formData,
    }),
  createProject: (formData) =>
    request(`${API_PREFIX}/projects/create`, {
      method: "POST",
      body: formData,
    }),
  uploadDocument: (formData) =>
    request(`${API_PREFIX}/documents/upload`, {
      method: "POST",
      body: formData,
    }),
  documentTask: (taskId) => request(`${API_PREFIX}/documents/${taskId}`),
  rerun: (taskId) =>
    request(`${API_PREFIX}/projects/${taskId}/rerun`, {
      method: "POST",
    }),
  deleteProject: (taskId) =>
    request(`${API_PREFIX}/projects/${taskId}`, {
      method: "DELETE",
    }),
  downloadUrl: (taskId, filename) =>
    `${API_BASE}${API_PREFIX}/projects/${taskId}/download/${encodeURIComponent(filename)}?token=${encodeURIComponent(getToken())}`,
};
