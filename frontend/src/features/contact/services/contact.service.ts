import { supabase } from "../../../lib/supabase";

type ContactSubmissionInput = {
  name: string;
  email: string;
  subject?: string;
  message: string;
};

export async function submitContactMessage(input: ContactSubmissionInput) {
  return supabase.from("contact_submissions").insert({
    name: input.name,
    email: input.email,
    subject: input.subject || null,
    message: input.message,
  });
}
