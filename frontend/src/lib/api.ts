const BASE = "/api";

export interface User {
  id: string;
  username: string;
  email: string | null;
  mfa_enabled: boolean;
  created_at: string;
}

export interface Person {
  id: string;
  user_id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  job_title: string;
  location: string;
  linkedin_url: string;
  twitter_handle: string;
  website: string;
  details: string;
  how_we_met: string;
  profile_image_url: string;
  birthday: string;
  anniversary: string;
  met_at: string;
  tags: string[];
  next_follow_up: string;
  follow_up_frequency_days: number;
  relationship_score: number;
  relationship_status: string;
  last_interaction_at: string;
  interaction_count: number;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: string;
  person_id: string;
  user_id: string;
  content: string;
  note_type: string;
  created_at: string;
}

export interface ActivityItem {
  note: Note;
  person_name: string;
  person_id: string;
}

export interface DashboardStats {
  total_contacts: number;
  status_counts: Record<string, number>;
  due_followups: number;
  tag_counts: Record<string, number>;
  cold_contacts: number;
  added_this_week: number;
  added_this_month: number;
  recent_contacts: Person[];
}

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

async function refreshAccessToken(): Promise<boolean> {
  const rt = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
  if (!rt) return false;
  try {
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: rt }),
    });
    if (!res.ok) return false;
    const body = await res.json();
    const data = body.data ?? body;
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let res = await fetch(url, { ...init, headers: { ...getHeaders(), ...init?.headers } });

  if (res.status === 401 && typeof window !== "undefined" && localStorage.getItem("refresh_token")) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      res = await fetch(url, { ...init, headers: { ...getHeaders(), ...init?.headers } });
    }
  }

  if (res.status === 401 && typeof window !== "undefined") {
    auth.clearLocal();
    window.location.href = "/auth/login";
    throw new ApiError("Unauthorized", 401);
  }

  const body = await res.json();

  if (!res.ok || body.success === false) {
    throw new ApiError(body.error || body.message || res.statusText, res.status, body.error_code);
  }

  return body.data !== undefined ? body.data : body;
}

export const auth = {
  async login(username: string, password: string) {
    return request<{ access_token: string; refresh_token: string; user: User }>(
      `${BASE}/auth/login`,
      { method: "POST", body: JSON.stringify({ username, password }) },
    );
  },

  async register(username: string, password: string, confirmPassword: string, email?: string) {
    return request<{ access_token: string; refresh_token: string; user: User }>(
      `${BASE}/auth/register`,
      {
        method: "POST",
        body: JSON.stringify({
          username,
          password,
          confirm_password: confirmPassword,
          email: email || undefined,
        }),
      },
    );
  },

  async refresh(refreshToken: string) {
    return request<{ access_token: string; refresh_token: string }>(
      `${BASE}/auth/refresh`,
      { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) },
    );
  },

  async logout(refreshToken?: string) {
    return request<void>(`${BASE}/auth/logout`, {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  },

  async me() {
    return request<User>(`${BASE}/auth/me`);
  },

  clearLocal() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },
};

export const people = {
  async list(tag?: string) {
    const qs = tag ? `?tag=${encodeURIComponent(tag)}` : "";
    return request<Person[]>(`${BASE}/people${qs}`);
  },

  async get(id: string) {
    return request<Person>(`${BASE}/people/${id}`);
  },

  async search(query: string) {
    return request<Person[]>(`${BASE}/people/search/${encodeURIComponent(query)}`);
  },

  async create(data: Partial<Person>) {
    return request<Person>(`${BASE}/people`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async update(id: string, data: Partial<Person>) {
    return request<Person>(`${BASE}/people/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async delete(id: string) {
    return request<void>(`${BASE}/people/${id}`, { method: "DELETE" });
  },

  async tags() {
    return request<string[]>(`${BASE}/people/tags`);
  },

  async dashboardStats() {
    return request<DashboardStats>(`${BASE}/people/dashboard/stats`);
  },

  async followups() {
    return request<Person[]>(`${BASE}/people/followups`);
  },
};

export const notes = {
  async list(personId: string) {
    return request<Note[]>(`${BASE}/notes/person/${personId}`);
  },

  async create(personId: string, content: string, noteType: string = "general") {
    return request<Note>(`${BASE}/notes/person/${personId}`, {
      method: "POST",
      body: JSON.stringify({ content, note_type: noteType }),
    });
  },

  async delete(noteId: string) {
    return request<void>(`${BASE}/notes/${noteId}`, { method: "DELETE" });
  },

  async activity(limit: number = 20) {
    return request<ActivityItem[]>(`${BASE}/notes/activity?limit=${limit}`);
  },
};

export const ai = {
  async summary(personId: string) {
    return request<{ summary: string }>(`${BASE}/people/${personId}/summary`, {
      method: "POST",
    });
  },

  async ask(question: string) {
    return request<{ answer: string }>(`${BASE}/ask`, {
      method: "POST",
      body: JSON.stringify({ question }),
    });
  },

  async suggestTags(personId: string) {
    return request<{ tags: string[] }>(`${BASE}/people/${personId}/suggest-tags`, {
      method: "POST",
    });
  },
};
