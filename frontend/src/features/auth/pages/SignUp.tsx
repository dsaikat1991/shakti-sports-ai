import AuthCard from "../components/AuthCard";
import AuthForm from "../components/AuthForm";

export default function SignUp() {
  return (
    <AuthCard
      eyebrow="Join Shakti"
      title="Create account"
      subtitle="Start as an athlete, coach, or academy and complete your profile next."
    >
      <AuthForm mode="signup" />
    </AuthCard>
  );
}