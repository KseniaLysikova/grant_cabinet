const API_BASE = "http://127.0.0.1:8000";

export function getToken() {
  return localStorage.getItem("token");
}

export function setToken(token) {
  localStorage.setItem("token", token);
}

export function clearToken() {
  localStorage.removeItem("token");
}

async function request(path, options = {}) {
  const token = getToken();

  const headers = {
    ...(options.headers || {})
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    if (Array.isArray(data.detail)) {
      const message = data.detail
        .map((item) => `${item.loc?.join(" -> ")}: ${item.msg}`)
        .join("; ");
      throw new Error(message);
    }

    throw new Error(data.detail || "Ошибка запроса");
  }

  return data;
}

export const api = {
  login: (payload) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  register: (payload) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  me: () => request("/auth/me"),

  getCompetitions: () => request("/competitions"),

  getApplications: () => request("/applications"),

  getApplication: (id) => request(`/applications/${id}`),

  createApplication: (payload) =>
    request("/applications", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  updateApplication: (id, payload) =>
    request(`/applications/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload)
    }),

  deleteApplication: (id) =>
    request(`/applications/${id}`, {
      method: "DELETE"
    }),

  uploadFile: (id, file) => {
    const formData = new FormData();
    formData.append("file", file);

    return request(`/applications/${id}/files`, {
      method: "POST",
      body: formData
    });
  },

  getAiReview: (id) => request(`/applications/${id}/ai-review`),

  updateStatus: (id, status) =>
    request(`/admin/applications/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    }),

  downloadFile: async (applicationId, fileId, filename) => {
    const token = getToken();

    const response = await fetch(
      `${API_BASE}/applications/${applicationId}/files/${fileId}/download`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || "Не удалось скачать файл");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
};