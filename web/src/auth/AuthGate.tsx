import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { readSession } from "./session";

interface Props {
  children: ReactNode;
}

export default function AuthGate({ children }: Props) {
  return readSession() ? <>{children}</> : <Navigate to="/users/login" replace />;
}
