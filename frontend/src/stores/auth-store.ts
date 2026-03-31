import { create } from "zustand";
import { auth, type User } from "@/lib/api";

interface AuthState {
  user: User | null;
  loading: boolean;
  setUser: (user: User | null) => void;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string, confirmPassword: string, email?: string) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,

  setUser: (user) => set({ user }),

  login: async (username, password) => {
    const data = await auth.login(username, password);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    set({ user: data.user });
  },

  register: async (username, password, confirmPassword, email?) => {
    const data = await auth.register(username, password, confirmPassword, email);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    set({ user: data.user });
  },

  logout: async () => {
    const rt = localStorage.getItem("refresh_token") ?? undefined;
    try {
      await auth.logout(rt);
    } catch {
      /* ignore */
    }
    auth.clearLocal();
    set({ user: null });
  },

  loadUser: async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      set({ user: null, loading: false });
      return;
    }
    try {
      const user = await auth.me();
      set({ user, loading: false });
    } catch {
      auth.clearLocal();
      set({ user: null, loading: false });
    }
  },
}));
