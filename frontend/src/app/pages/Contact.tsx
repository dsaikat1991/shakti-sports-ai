import { useState } from "react";
import { Mail } from "lucide-react";
import Container from "../../components/ui/Container";
import { submitContactMessage } from "../../features/contact/services/contact.service";

const CONTACT_EMAIL = "contact@shaktisportsai.com";

export default function Contact() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [submitting, setSubmitting] = useState(false);

  function updateField(field: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (submitting) return;
    setSubmitting(true);

    // Durable backstop first (best-effort - a mailto: navigation below
    // still happens even if this fails, e.g. Supabase is briefly down).
    const { error } = await submitContactMessage(form);
    if (error) {
      console.error("Failed to store contact submission:", error);
    }

    const subject = form.subject || "Message from Shakti Sports AI website";

    const body = [
      form.message,
      "",
      "---",
      `From: ${form.name}`,
      `Email: ${form.email}`,
    ].join("\n");

    const mailtoUrl = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(
      subject,
    )}&body=${encodeURIComponent(body)}`;

    setSubmitting(false);
    window.location.href = mailtoUrl;
  }

  return (
    <div className="bg-surface-canvas py-20">
      <Container className="max-w-2xl">
        <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-brand-action">
          Contact
        </p>

        <h1 className="mt-4 text-2xl font-bold text-text-primary md:text-3xl">
          Get in touch.
        </h1>

        <p className="mt-4 text-base leading-7 text-text-secondary">
          Questions, feedback, or partnership ideas — we'd love to hear from
          you.
        </p>

        <a
          href={`mailto:${CONTACT_EMAIL}`}
          className="mt-4 inline-flex items-center gap-2 text-sm font-bold text-brand-action hover:underline"
        >
          <Mail className="h-4 w-4" />
          {CONTACT_EMAIL}
        </a>

        <form
          onSubmit={handleSubmit}
          className="mt-10 space-y-4 rounded-4xl border border-border-default bg-surface-card p-8 shadow-2xl shadow-border-default/70"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <input
              required
              value={form.name}
              onChange={(e) => updateField("name", e.target.value)}
              placeholder="Your name"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />

            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => updateField("email", e.target.value)}
              placeholder="Your email"
              className="rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
            />
          </div>

          <input
            value={form.subject}
            onChange={(e) => updateField("subject", e.target.value)}
            placeholder="Subject"
            className="w-full rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
          />

          <textarea
            required
            value={form.message}
            onChange={(e) => updateField("message", e.target.value)}
            placeholder="How can we help?"
            rows={6}
            className="w-full rounded-xl border border-border-default px-4 py-3 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
          />

          <button
            type="submit"
            disabled={submitting}
            className="w-full cursor-pointer rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Sending..." : "Send Message"}
          </button>

          <p className="text-center text-xs text-text-disabled">
            This opens your email app with your message ready to send to{" "}
            {CONTACT_EMAIL}.
          </p>
        </form>
      </Container>
    </div>
  );
}
