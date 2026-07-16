import { describe, expect, it } from "vitest";

import { validateAvatarFile } from "./avatar.service";

function makeFile(sizeBytes: number, type: string): File {
  return new File([new Uint8Array(sizeBytes)], "photo", { type });
}

describe("validateAvatarFile", () => {
  it("accepts a valid JPEG under the size limit", () => {
    const file = makeFile(1024, "image/jpeg");
    expect(validateAvatarFile(file)).toBeNull();
  });

  it("accepts PNG and WebP too", () => {
    expect(validateAvatarFile(makeFile(1024, "image/png"))).toBeNull();
    expect(validateAvatarFile(makeFile(1024, "image/webp"))).toBeNull();
  });

  it("rejects a non-image type", () => {
    const file = makeFile(1024, "application/pdf");
    expect(validateAvatarFile(file)).toMatch(/JPEG, PNG, or WebP/i);
  });

  it("rejects a file over 5MB", () => {
    const file = makeFile(5 * 1024 * 1024 + 1, "image/jpeg");
    expect(validateAvatarFile(file)).toMatch(/5MB/);
  });

  it("accepts a file exactly at the 5MB limit", () => {
    const file = makeFile(5 * 1024 * 1024, "image/jpeg");
    expect(validateAvatarFile(file)).toBeNull();
  });
});
