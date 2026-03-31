"use client";
import Link from "next/link";
import { Building2, MapPin, Phone, Mail } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { Person } from "@/lib/api";

const STATUS_COLORS: Record<string, "green" | "yellow" | "red" | "gray"> = {
  active: "green", strong: "green",
  warm: "yellow", growing: "yellow",
  cold: "red", fading: "red",
};

export function ContactCard({ person }: { person: Person }) {
  const initials = person.name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <Link href={`/contacts/${person.id}`}>
      <Card className="hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-800 transition-all cursor-pointer h-full">
        <div className="flex items-start gap-4">
          <div className="h-12 w-12 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-bold text-sm shrink-0">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-gray-900 dark:text-white truncate">{person.name}</h3>
            {person.job_title && (
              <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{person.job_title}</p>
            )}
          </div>
          <Badge color={STATUS_COLORS[person.relationship_status] ?? "gray"}>
            {person.relationship_status}
          </Badge>
        </div>

        <div className="mt-3 space-y-1.5 text-sm text-gray-600 dark:text-gray-400">
          {person.company && (
            <div className="flex items-center gap-2 truncate">
              <Building2 size={14} className="shrink-0" /> {person.company}
            </div>
          )}
          {person.location && (
            <div className="flex items-center gap-2 truncate">
              <MapPin size={14} className="shrink-0" /> {person.location}
            </div>
          )}
          {person.email && (
            <div className="flex items-center gap-2 truncate">
              <Mail size={14} className="shrink-0" /> {person.email}
            </div>
          )}
          {person.phone && (
            <div className="flex items-center gap-2 truncate">
              <Phone size={14} className="shrink-0" /> {person.phone}
            </div>
          )}
        </div>

        {person.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {person.tags.slice(0, 4).map((t) => (
              <Badge key={t} color="indigo">{t}</Badge>
            ))}
            {person.tags.length > 4 && <Badge color="gray">+{person.tags.length - 4}</Badge>}
          </div>
        )}
      </Card>
    </Link>
  );
}
