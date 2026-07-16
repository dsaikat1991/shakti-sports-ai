import { supabase } from "../../../lib/supabase";

export const AVATAR_BUCKET_NAME = "avatars";

const MAX_AVATAR_SIZE_BYTES = 5 * 1024 * 1024;
const ALLOWED_AVATAR_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"];

// Avatars are shown often (Profile, UserMenu on every page) rather than
// downloaded once like a video - a longer expiry than
// analysis.service.ts's SIGNED_URL_EXPIRY_SECONDS avoids re-signing on
// every render.
const AVATAR_SIGNED_URL_EXPIRY_SECONDS = 3600;

function avatarStoragePath(userId: string): string {
  return `${userId}/avatar`;
}

// Pure validation, no I/O - easy to unit test and reused by any future
// upload entry point without duplicating the rules.
export function validateAvatarFile(file: File): string | null {
  if (!ALLOWED_AVATAR_MIME_TYPES.includes(file.type)) {
    return "Please choose a JPEG, PNG, or WebP image.";
  }

  if (file.size > MAX_AVATAR_SIZE_BYTES) {
    return "Image must be under 5MB.";
  }

  return null;
}

// Fixed key per user + upsert:true - a re-upload always replaces the
// same object rather than accumulating orphaned files with different
// extensions. Storage RLS (migration 0008) restricts this to the
// caller's own folder regardless.
export async function uploadAvatar(userId: string, file: File): Promise<string> {
  const validationError = validateAvatarFile(file);
  if (validationError) {
    throw new Error(validationError);
  }

  const path = avatarStoragePath(userId);

  const { error: uploadError } = await supabase.storage
    .from(AVATAR_BUCKET_NAME)
    .upload(path, file, { upsert: true, contentType: file.type, cacheControl: "3600" });

  if (uploadError) {
    throw new Error(uploadError.message);
  }

  const { error: profileError } = await supabase
    .from("profiles")
    .update({ avatar_url: path })
    .eq("id", userId);

  if (profileError) {
    throw new Error(profileError.message);
  }

  return path;
}

export async function removeAvatar(userId: string, path: string): Promise<void> {
  const { error: storageError } = await supabase.storage
    .from(AVATAR_BUCKET_NAME)
    .remove([path]);

  if (storageError) {
    throw new Error(storageError.message);
  }

  const { error: profileError } = await supabase
    .from("profiles")
    .update({ avatar_url: null })
    .eq("id", userId);

  if (profileError) {
    throw new Error(profileError.message);
  }
}

// Mirrors analysis.service.ts's createSignedVideoUrl - same private-
// bucket-plus-signed-URL pattern, different bucket/expiry.
export async function getAvatarSignedUrl(path: string): Promise<string> {
  const { data, error } = await supabase.storage
    .from(AVATAR_BUCKET_NAME)
    .createSignedUrl(path, AVATAR_SIGNED_URL_EXPIRY_SECONDS);

  if (error || !data?.signedUrl) {
    throw new Error(error?.message || "Could not create a signed avatar URL.");
  }

  return data.signedUrl;
}
