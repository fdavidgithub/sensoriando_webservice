import { type ReactNode, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import Loading from "../components/Loading";
import { ensureIdToken } from "../api/client";
import { readSession } from "./session";

interface Props {
  children: ReactNode;
}

type Status = "checking" | "allowed" | "denied";

/**
 * The gate in front of every private screen.
 *
 * It cannot decide synchronously any more. The id token lives in memory, so a
 * reload leaves a valid session with no token at all -- and rendering the
 * children in that state would make the first request of every screen a 401.
 * The gate renews first and only then lets them through.
 */
export default function AuthGate({ children }: Props) {
  const [status, setStatus] = useState<Status>(() =>
    readSession() ? "checking" : "denied",
  );

  useEffect(() => {
    if (status !== "checking") return;

    let active = true;
    ensureIdToken()
      .then(() => {
        if (active) setStatus("allowed");
      })
      .catch(() => {
        // The refresh token is gone or past its 30 days. clearSession has
        // already run inside the client; there is nothing to do but ask for
        // the OTP again.
        if (active) setStatus("denied");
      });

    return () => {
      active = false;
    };
  }, [status]);

  if (status === "checking") return <Loading />;
  if (status === "denied") return <Navigate to="/users/login" replace />;

  return <>{children}</>;
}