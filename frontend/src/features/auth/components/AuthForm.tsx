import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthDivider from "./AuthDivider";
import GoogleButton from "./GoogleButton";
import { useAuthActions } from "../hooks/useAuthActions";
import { getUserRole } from "../services/profile.service";
import type { AuthMode } from "../types/auth";
import { ROUTES, roleHomeRoute } from "../../../constants/routes";

type Props = {
  mode: AuthMode;
};

export default function AuthForm({ mode }: Props) {
  const navigate = useNavigate();
  const { signIn, signUp } = useAuthActions();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const isSignIn = mode === "signin";

async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
  event.preventDefault();

  setLoading(true);
  setErrorMessage("");

  if (isSignIn) {
    const { data, error } = await signIn(email, password);

    if (error) {
      setLoading(false);
      setErrorMessage(error.message);
      return;
    }

    const role = data.user ? await getUserRole(data.user.id) : null;

    setLoading(false);
    navigate(roleHomeRoute(role));
    return;
  }

  const { error } = await signUp(email, password);

  setLoading(false);

  if (error) {
    setErrorMessage(error.message);
    return;
  }

  navigate(ROUTES.AUTH.CHOOSE_ROLE);
}

  return (
    <>
      <GoogleButton />

      <AuthDivider />

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-sm font-semibold text-text-primary">
            Email
          </label>

          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            className="mt-2 w-full rounded-xl border border-border-default px-4 py-3 text-sm outline-none transition focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
          />
        </div>

        <div>
          <label className="text-sm font-semibold text-text-primary">
            Password
          </label>

          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Minimum 6 characters"
            className="mt-2 w-full rounded-xl border border-border-default px-4 py-3 text-sm outline-none transition focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
          />
        </div>

        {errorMessage && (
          <div className="rounded-xl bg-error-failure-soft px-4 py-3 text-sm font-medium text-error-failure">
            {errorMessage}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full cursor-pointer rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading
            ? "Please wait..."
            : isSignIn
              ? "Sign In"
              : "Create Account"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-text-secondary">
        {isSignIn ? "Don't have an account?" : "Already have an account?"}{" "}
        <Link
          to={isSignIn ? ROUTES.AUTH.SIGN_UP : ROUTES.AUTH.SIGN_IN}
          className="font-bold text-brand-action hover:underline"
        >
          {isSignIn ? "Create one" : "Sign in"}
        </Link>
      </p>
    </>
  );
}