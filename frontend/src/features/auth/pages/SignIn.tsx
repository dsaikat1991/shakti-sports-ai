import AuthCard from "../components/AuthCard";
import AuthForm from "../components/AuthForm";

export default function SignIn() {
  return (
    <AuthCard
      eyebrow="Welcome back"
      title="Sign in"
      subtitle="Continue building India's next performance intelligence platform."
    >
      <AuthForm mode="signin" />
    </AuthCard>
  );
}