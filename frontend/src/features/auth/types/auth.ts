export interface AuthFormData {
  email: string;
  password: string;
}

export type UserRole = "athlete" | "coach" | "academy" | "admin";

export type AuthMode = "signin" | "signup";