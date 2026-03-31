"use client";
import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Building2, Edit, Mail, MapPin, Phone, Sparkles, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Modal } from "@/components/ui/modal";
import { ContactForm } from "@/components/contacts/contact-form";
import { ai, notes as notesApi, people, type Note, type Person, ApiError } from "@/lib/api";

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [person, setPerson] = useState<Person | null>(null);
  const [contactNotes, setContactNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [noteType, setNoteType] = useState("general");
  const [aiSummary, setAiSummary] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const load = useCallback(async () => {
    try {
      const [p, n] = await Promise.all([people.get(id), notesApi.list(id)]);
      setPerson(p);
      setContactNotes(n);
    } catch {
      toast.error("Contact not found");
      router.push("/contacts");
    } finally {
      setLoading(false);
    }
  }, [id, router]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleAddNote(e: React.FormEvent) {
    e.preventDefault();
    if (!noteText.trim()) return;
    try {
      await notesApi.create(id, noteText, noteType);
      setNoteText("");
      toast.success("Note added");
      load();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to add note");
    }
  }

  async function handleDeleteNote(noteId: string) {
    try {
      await notesApi.delete(noteId);
      toast.success("Note deleted");
      load();
    } catch {
      toast.error("Failed to delete");
    }
  }

  async function handleDelete() {
    if (!confirm("Delete this contact? This cannot be undone.")) return;
    try {
      await people.delete(id);
      toast.success("Contact deleted");
      router.push("/contacts");
    } catch {
      toast.error("Failed to delete");
    }
  }

  async function handleAiSummary() {
    setAiLoading(true);
    setAiSummary(null);
    try {
      const res = await ai.summary(id);
      setAiSummary(res.summary);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "AI unavailable");
    } finally {
      setAiLoading(false);
    }
  }

  if (loading || !person) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  const initials = person.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.push("/contacts")}>
          <ArrowLeft size={16} />
        </Button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex-1">{person.name}</h1>
        <Button variant="secondary" size="sm" onClick={() => setEditing(true)}>
          <Edit size={14} className="mr-1" /> Edit
        </Button>
        <Button variant="danger" size="sm" onClick={handleDelete}>
          <Trash2 size={14} />
        </Button>
      </div>

      {/* Profile card */}
      <Card>
        <div className="flex items-start gap-5">
          <div className="h-16 w-16 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-bold text-xl shrink-0">
            {initials}
          </div>
          <div className="flex-1 min-w-0 space-y-2">
            {person.job_title && <p className="text-lg text-gray-700 dark:text-gray-300">{person.job_title}</p>}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600 dark:text-gray-400">
              {person.company && <span className="flex items-center gap-2"><Building2 size={14} /> {person.company}</span>}
              {person.location && <span className="flex items-center gap-2"><MapPin size={14} /> {person.location}</span>}
              {person.email && <span className="flex items-center gap-2"><Mail size={14} /> {person.email}</span>}
              {person.phone && <span className="flex items-center gap-2"><Phone size={14} /> {person.phone}</span>}
            </div>
            {person.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 pt-1">
                {person.tags.map((t) => <Badge key={t} color="indigo">{t}</Badge>)}
              </div>
            )}
          </div>
          <div className="text-right shrink-0">
            <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
              {Math.round(person.relationship_score)}
            </p>
            <p className="text-xs text-gray-500 capitalize">{person.relationship_status}</p>
          </div>
        </div>

        {person.details && (
          <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{person.details}</p>
          </div>
        )}
      </Card>

      {/* AI Summary */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Blueprint</h2>
          <Button size="sm" variant="secondary" onClick={handleAiSummary} disabled={aiLoading}>
            <Sparkles size={14} className="mr-1" /> {aiLoading ? "Generating..." : "Generate"}
          </Button>
        </div>
        {aiSummary ? (
          <div className="prose dark:prose-invert max-w-none text-sm" dangerouslySetInnerHTML={{ __html: aiSummary }} />
        ) : (
          <p className="text-sm text-gray-500">Click Generate to create an AI-powered relationship blueprint.</p>
        )}
      </Card>

      {/* Notes */}
      <Card>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Notes ({contactNotes.length})
        </h2>

        <form onSubmit={handleAddNote} className="flex gap-3 mb-4">
          <textarea
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            placeholder="Add a note..."
            rows={2}
            className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 text-sm dark:bg-gray-800 dark:text-white"
          />
          <div className="flex flex-col gap-2">
            <select
              value={noteType}
              onChange={(e) => setNoteType(e.target.value)}
              className="rounded-lg border border-gray-300 dark:border-gray-600 px-2 py-1 text-sm dark:bg-gray-800 dark:text-white"
            >
              <option value="general">General</option>
              <option value="meeting">Meeting</option>
              <option value="call">Call</option>
              <option value="email">Email</option>
              <option value="social">Social</option>
            </select>
            <Button size="sm" type="submit">Add</Button>
          </div>
        </form>

        <div className="space-y-3">
          {contactNotes.map((note) => (
            <div key={note.id} className="flex items-start gap-3 group">
              <div className="mt-1.5 h-2 w-2 rounded-full bg-indigo-500 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-800 dark:text-gray-200">{note.content}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  <Badge color="gray">{note.note_type}</Badge>
                  <span className="ml-2">{new Date(note.created_at).toLocaleDateString()}</span>
                </p>
              </div>
              <button
                onClick={() => handleDeleteNote(note.id)}
                className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
          {contactNotes.length === 0 && <p className="text-sm text-gray-500">No notes yet.</p>}
        </div>
      </Card>

      {/* Edit modal */}
      <Modal open={editing} onClose={() => setEditing(false)} title="Edit Contact" wide>
        <ContactForm
          person={person}
          onSaved={(p) => {
            setPerson(p);
            setEditing(false);
          }}
          onCancel={() => setEditing(false)}
        />
      </Modal>
    </div>
  );
}
