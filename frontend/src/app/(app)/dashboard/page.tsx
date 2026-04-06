"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Users, UserCheck, Bell, Tag } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { people, notes, type DashboardStats, type ActivityItem } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([people.dashboardStats(), notes.activity(10)])
      .then(([s, a]) => {
        setStats(s);
        setActivity(a);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={<Users size={24} />} label="Total Contacts" value={stats?.total_contacts ?? 0} color="indigo" />
        <StatCard
          icon={<UserCheck size={24} />}
          label="Active"
          value={stats?.status_counts?.active ?? 0}
          color="green"
        />
        <StatCard icon={<Bell size={24} />} label="Due Follow-ups" value={stats?.due_followups ?? 0} color="yellow" />
        <StatCard
          icon={<Tag size={24} />}
          label="Tags"
          value={Object.keys(stats?.tag_counts ?? {}).length}
          color="indigo"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Status breakdown */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Relationship Status</h2>
          <div className="space-y-3">
            {Object.entries(stats?.status_counts ?? {}).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">{status.replace(/_/g, " ")}</span>
                <Badge color={statusColor(status)}>{count}</Badge>
              </div>
            ))}
          </div>
        </Card>

        {/* Top tags */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Tags</h2>
          <div className="flex flex-wrap gap-2">
            {Object.entries(stats?.tag_counts ?? {})
              .sort(([, a], [, b]) => b - a)
              .slice(0, 15)
              .map(([tag, count]) => (
                <Link key={tag} href={`/contacts?tag=${encodeURIComponent(tag)}`}>
                  <Badge color="indigo" className="cursor-pointer">
                    {tag} ({count})
                  </Badge>
                </Link>
              ))}
          </div>
        </Card>

        {/* Recent activity */}
        <Card className="lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
          {activity.length === 0 ? (
            <p className="text-sm text-gray-500">No recent activity yet.</p>
          ) : (
            <div className="space-y-3">
              {activity.map((item) => (
                <div key={item.note.id} className="flex items-start gap-3 text-sm">
                  <div className="mt-1 h-2 w-2 rounded-full bg-indigo-500 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-800 dark:text-gray-200 truncate">{item.note.content}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {item.person_name} &middot; {item.note.note_type} &middot; {new Date(item.note.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) {
  const bg: Record<string, string> = {
    indigo: "bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400",
    green: "bg-green-50 text-green-600 dark:bg-green-950 dark:text-green-400",
    yellow: "bg-yellow-50 text-yellow-600 dark:bg-yellow-950 dark:text-yellow-400",
  };
  return (
    <Card className="flex items-center gap-4">
      <div className={`rounded-lg p-3 ${bg[color]}`}>{icon}</div>
      <div>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
      </div>
    </Card>
  );
}

function statusColor(s: string): "green" | "yellow" | "red" | "gray" | "indigo" {
  if (s === "active" || s === "strong") return "green";
  if (s === "warm" || s === "growing") return "yellow";
  if (s === "cold" || s === "fading") return "red";
  return "gray";
}
