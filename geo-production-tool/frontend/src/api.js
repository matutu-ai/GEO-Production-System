const API_BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `请求失败：${response.status}`);
  }
  return response.json();
}

export const api = {
  health: () => request("/api/health"),
  projects: () => request("/api/projects"),
  project: (taskId) => request(`/api/projects/${taskId}`),
  analyze: (formData) =>
    request("/api/analyze", {
      method: "POST",
      body: formData,
    }),
  downloadUrl: (taskId, filename) =>
    `${API_BASE}/api/projects/${taskId}/download/${encodeURIComponent(filename)}`,
};
