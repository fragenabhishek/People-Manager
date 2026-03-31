"use client";
import { Sidebar } from "@/components/layout/sidebar";
import { AuthGuard } from "@/components/layout/auth-guard";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 lg:ml-64 p-6 pt-16 lg:pt-6">{children}</main>
      </div>
    </AuthGuard>
  );
}
