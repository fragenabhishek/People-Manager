import { create } from "zustand";

interface AppState {
  tagFilter: string | null;
  setTagFilter: (tag: string | null) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  darkMode: boolean;
  toggleDarkMode: () => void;
  sidebarOpen: boolean;
  setSidebarOpen: (v: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  tagFilter: null,
  setTagFilter: (tag) => set({ tagFilter: tag }),
  searchQuery: "",
  setSearchQuery: (q) => set({ searchQuery: q }),
  darkMode: false,
  toggleDarkMode: () =>
    set((s) => {
      const next = !s.darkMode;
      if (typeof window !== "undefined") localStorage.setItem("darkMode", String(next));
      return { darkMode: next };
    }),
  sidebarOpen: false,
  setSidebarOpen: (v) => set({ sidebarOpen: v }),
}));
