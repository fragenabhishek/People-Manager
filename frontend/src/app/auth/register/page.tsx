"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth-store";
import { ApiError } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuthStore();
  const [form, setForm] = useState({ username: "", email: "", password: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      await register(form.username, form.password, form.confirmPassword, form.email || undefined);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 bg-gradient-to-br from-indigo-50 to-gray-100 dark:from-gray-950 dark:to-gray-900">
      <Card className="w-full max-w-md">
        <div className="text-center mb-6">
          <span className="text-4xl">👥</span>
          <h1 className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">Create account</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Start managing your relationships</p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-900/20 p-3 text-sm text-red-700 dark:text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Username" value={form.username} onChange={set("username")} required autoFocus />
          <Input label="Email (optional)" type="email" value={form.email} onChange={set("email")} />
          <Input label="Password" type="password" value={form.password} onChange={set("password")} required />
          <Input label="Confirm Password" type="password" value={form.confirmPassword} onChange={set("confirmPassword")} required />
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Creating..." : "Create account"}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
          Already have an account?{" "}
          <Link href="/auth/login" className="text-indigo-600 hover:underline dark:text-indigo-400">
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  );
}
