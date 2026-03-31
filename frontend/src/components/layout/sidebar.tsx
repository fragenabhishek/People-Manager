"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, Activity, MessageSquare, Moon, Sun, LogOut, Menu, X } from "lucide-react";
import { cn } from "@/lib/cn";
import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/contacts", label: "Contacts", icon: Users },
  { href: "/activity", label: "Activity", icon: Activity },
  { href: "/ask", label: "Ask AI", icon: MessageSquare },
];

export function Sidebar() {
  const pathname = usePathname();
  const { darkMode, toggleDarkMode, sidebarOpen, setSidebarOpen } = useAppStore();
  const { user, logout } = useAuthStore();

  return (
    <>
      {/* Mobile hamburger */}
      <button
        className="fixed top-4 left-4 z-50 lg:hidden rounded-lg bg-white dark:bg-gray-800 p-2 shadow-md"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-30 bg-black/30 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-transform lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-center gap-2 px-6 py-5 border-b border-gray-200 dark:border-gray-700">
          <span className="text-2xl">👥</span>
          <span className="text-lg font-bold text-gray-900 dark:text-white">People Manager</span>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  active
                    ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
                    : "text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800",
                )}
              >
                <item.icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-gray-200 dark:border-gray-700 px-3 py-4 space-y-2">
          <button
            onClick={toggleDarkMode}
            className="flex w-full items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800"
          >
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            {darkMode ? "Light mode" : "Dark mode"}
          </button>

          {user && (
            <div className="flex items-center gap-3 px-3 py-2">
              <div className="h-8 w-8 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-xs font-bold text-indigo-700 dark:text-indigo-300">
                {user.username[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{user.username}</p>
              </div>
              <button
                onClick={() => { logout(); window.location.href = "/auth/login"; }}
                className="text-gray-400 hover:text-red-500"
                title="Logout"
              >
                <LogOut size={16} />
              </button>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
