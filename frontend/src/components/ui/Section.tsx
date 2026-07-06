import type { ReactNode } from "react";
import Container from "./Container";

interface Props {
  children: ReactNode;
  className?: string;
}

export default function Section({
  children,
  className = "",
}: Props) {
  return (
    <section className={`py-24 ${className}`}>
      <Container>{children}</Container>
    </section>
  );
}