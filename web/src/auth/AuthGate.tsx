import { type ReactNode, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import Loading from "../components/Loading";
import { ensureIdToken, SESSION_EXPIRED } from "../api/client";
import { onSessionExpired, readSession } from "./session";

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
 *
 * Letting a screen through is not the end of the story: the refresh token can
 * still expire, or the API can still reject it, while the screen is already
 * open. client.ts calls notifySessionExpired() when that happens, which is
 * how an AuthGate that already rendered its children learns to send the user
 * back to login instead of leaving them on a screen that keeps failing.
 */
export default function AuthGate({ children }: Props) {
  const [status, setStatus] = useState<Status>(() =>
    readSession() ? "checking" : "denied",
  );
  const [deniedReason, setDeniedReason] = useState<string | null>(null);

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

  useEffect(() => {
    if (status !== "allowed") return;

    return onSessionExpired(() => {
      setDeniedReason(SESSION_EXPIRED);
      setStatus("denied");
    });
  }, [status]);

  if (status === "checking") return <Loading />;
  if (status === "denied") {
    return (
      <Navigate
        to="/users/login"
        replace
        state={deniedReason ? { message: deniedReason } : undefined}
      />
    );
  }

  return <>{children}</>;
}