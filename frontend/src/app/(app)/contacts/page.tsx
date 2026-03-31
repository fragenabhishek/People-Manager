"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Plus, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Modal } from "@/components/ui/modal";
import { ContactCard } from "@/components/contacts/contact-card";
import { ContactForm } from "@/components/contacts/contact-form";
import { people, type Person } from "@/lib/api";

export default function ContactsPage() {
  const searchParams = useSearchParams();
  const tagFromUrl = searchParams.get("tag");

  const [contacts, setContacts] = useState<Person[]>([]);
  const [allTags, setAllTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [tagFilter, setTagFilter] = useState<string | null>(tagFromUrl);
  const [showForm, setShowForm] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [list, tags] = await Promise.all([people.list(tagFilter ?? undefined), people.tags()]);
      setContacts(list);
      setAllTags(tags);
    } catch {
      /* handled by api layer */
    } finally {
      setLoading(false);
    }
  }, [tagFilter]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (tagFromUrl !== tagFilter) setTagFilter(tagFromUrl);
  }, [tagFromUrl]);

  const filtered = useMemo(() => {
    if (!search.trim()) return contacts;
    const q = search.toLowerCase();
    return contacts.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.company?.toLowerCase().includes(q) ||
        p.email?.toLowerCase().includes(q) ||
        p.job_title?.toLowerCase().includes(q),
    );
  }, [contacts, search]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Contacts {tagFilter && <Badge color="indigo" className="ml-2">{tagFilter}</Badge>}
        </h1>
        <Button onClick={() => setShowForm(true)}>
          <Plus size={16} className="mr-1" /> Add Contact
        </Button>
      </div>

      {/* Search + tag filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search contacts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {tagFilter && (
            <Badge color="red" onClick={() => setTagFilter(null)}>
              Clear filter &times;
            </Badge>
          )}
          {allTags.slice(0, 8).map((t) => (
            <Badge
              key={t}
              color={t === tagFilter ? "indigo" : "gray"}
              onClick={() => setTagFilter(t === tagFilter ? null : t)}
            >
              {t}
            </Badge>
          ))}
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-500 dark:text-gray-400">
          <p className="text-lg">No contacts found</p>
          <p className="text-sm mt-1">Try adjusting your search or add a new contact</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((p) => (
            <ContactCard key={p.id} person={p} />
          ))}
        </div>
      )}

      {/* Create modal */}
      <Modal open={showForm} onClose={() => setShowForm(false)} title="Add Contact" wide>
        <ContactForm
          onSaved={() => {
            setShowForm(false);
            load();
          }}
          onCancel={() => setShowForm(false)}
        />
      </Modal>
    </div>
  );
}
