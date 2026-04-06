"use client";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { notes as notesApi, type ActivityItem } from "@/lib/api";

export default function ActivityPage() {
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    notesApi
      .activity(50)
      .then(setActivity)
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
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Activity Feed</h1>

      {activity.length === 0 ? (
        <Card>
          <p className="text-center text-gray-500 py-8">No activity yet. Add notes to contacts to see them here.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {activity.map((item) => (
            <Card key={item.note.id} className="py-4">
              <div className="flex items-start gap-3">
                <div className="mt-1 h-2 w-2 rounded-full bg-indigo-500 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-800 dark:text-gray-200">{item.note.content}</p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-300">{item.person_name}</span>
                    <Badge color="gray">{item.note.note_type}</Badge>
                    <span className="text-xs text-gray-400">
                      {new Date(item.note.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
