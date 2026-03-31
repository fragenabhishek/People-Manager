"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { people, type Person, ApiError } from "@/lib/api";
import { toast } from "sonner";

interface Props {
  person?: Person;
  onSaved: (p: Person) => void;
  onCancel: () => void;
}

export function ContactForm({ person, onSaved, onCancel }: Props) {
  const isEdit = !!person;
  const [form, setForm] = useState({
    name: person?.name ?? "",
    email: person?.email ?? "",
    phone: person?.phone ?? "",
    company: person?.company ?? "",
    job_title: person?.job_title ?? "",
    location: person?.location ?? "",
    details: person?.details ?? "",
    how_we_met: person?.how_we_met ?? "",
    tags: person?.tags?.join(", ") ?? "",
    linkedin_url: person?.linkedin_url ?? "",
    twitter_handle: person?.twitter_handle ?? "",
    website: person?.website ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSaving(true);
    const payload = {
      ...form,
      tags: form.tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
    };
    try {
      const saved = isEdit ? await people.update(person!.id, payload) : await people.create(payload);
      toast.success(isEdit ? "Contact updated" : "Contact created");
      onSaved(saved);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="rounded-lg bg-red-50 dark:bg-red-900/20 p-3 text-sm text-red-700 dark:text-red-400">{error}</div>}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input label="Name *" value={form.name} onChange={set("name")} required autoFocus />
        <Input label="Email" value={form.email} onChange={set("email")} type="email" />
        <Input label="Phone" value={form.phone} onChange={set("phone")} />
        <Input label="Company" value={form.company} onChange={set("company")} />
        <Input label="Job Title" value={form.job_title} onChange={set("job_title")} />
        <Input label="Location" value={form.location} onChange={set("location")} />
        <Input label="LinkedIn" value={form.linkedin_url} onChange={set("linkedin_url")} placeholder="https://linkedin.com/in/..." />
        <Input label="Twitter" value={form.twitter_handle} onChange={set("twitter_handle")} placeholder="@handle" />
        <Input label="Website" value={form.website} onChange={set("website")} />
        <Input label="Tags (comma-separated)" value={form.tags} onChange={set("tags")} placeholder="mentor, vip, tech" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">How You Met</label>
        <textarea
          value={form.how_we_met}
          onChange={set("how_we_met")}
          rows={2}
          className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 text-sm dark:bg-gray-800 dark:text-white"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Details / Notes</label>
        <textarea
          value={form.details}
          onChange={set("details")}
          rows={3}
          className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 text-sm dark:bg-gray-800 dark:text-white"
        />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button type="submit" disabled={saving}>
          {saving ? "Saving..." : isEdit ? "Update Contact" : "Add Contact"}
        </Button>
      </div>
    </form>
  );
}
