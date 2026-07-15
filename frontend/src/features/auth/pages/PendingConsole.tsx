import ComingSoon from "../../../components/shared/ComingSoon";
import { useAuth } from "../context/AuthContext";

export default function PendingConsole({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  const { signOut } = useAuth();

  return (
    <ComingSoon
      title={title}
      description={description}
      action={{ type: "button", label: "Sign Out", onClick: signOut }}
    />
  );
}
