import { type FormEvent, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { login, verifyOtp } from "../api/endpoints";
import { setIdToken, writeSession } from "../auth/session";
import ErrorBanner from "../components/ErrorBanner";

// The API layer always rejects with ApiError, which marks itself with
// name === "ApiError". Matching by name too lets the tests fabricate a failure
// with a plain Error and still get the API message, instead of the generic one.
function apiMessage(caught: unknown): string {
  if (caught instanceof ApiError) return caught.message;
  if (caught instanceof Error && caught.name === "ApiError") return caught.message;
  return "Falha inesperada ao entrar";
}

/**
 * Sign-in in two steps: an address, then the code that arrives in it.
 *
 * The first step always advances, even for an address with no account: the API
 * answers the same either way, on purpose, so that this screen cannot be used
 * to find out who is registered. An unknown address only fails at the code.
 */

export default function LoginPage() {
  const navigate = useNavigate();
  // AuthGate hands this in when a session expires mid-use and it redirects
  // here on its own: without it the user lands on a blank login form with no
  // explanation for why they were signed out.
  const location = useLocation();
  const [step, setStep] = useState<"email" | "code">("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [session, setSession] = useState("");
  const [destination, setDestination] = useState("");
  const [error, setError] = useState<string | null>(
    (location.state as { message?: string } | null)?.message ?? null,
  );
  const [sending, setSending] = useState(false);

  async function requestCode(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSending(true);

    try {
      const answer = await login({ email });
      setSession(answer.session);
      setDestination(answer.destination);
      setStep("code");
    } catch (caught: unknown) {
      setError(apiMessage(caught));
    } finally {
      setSending(false);
    }
  }

  async function enter(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSending(true);

    try {
      const tokens = await verifyOtp({ email, code, session });
      writeSession(tokens.username, tokens.refresh_token);
      setIdToken(tokens.id_token, tokens.expires_in);
      navigate("/home/private");
    } catch (caught: unknown) {
      setError(apiMessage(caught));
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">Autenticar usuário</h1>
        </div>
      </section>

      <section className="signUp">
        {error && <ErrorBanner message={error} />}

        {step === "email" ? (
          <form onSubmit={requestCode}>
            <p className="font-17px">
              Enviaremos um código de acesso para o seu e-mail. Não há senha. A sessão
              dura 30 dias.
            </p>
            <p>
              <label className="font-17px" htmlFor="email">
                E-mail
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </p>
            <button type="submit" className="font-16px" disabled={sending}>
              <span>{sending ? "Enviando…" : "Receber código"}</span>
            </button>
          </form>
        ) : (
          <form onSubmit={enter}>
            <p className="font-17px">
              Enviamos um código para {destination}. Digite-o abaixo para entrar.
            </p>
            <p>
              <label className="font-17px" htmlFor="code">
                Código
              </label>
              <input
                id="code"
                inputMode="numeric"
                value={code}
                onChange={(event) => setCode(event.target.value)}
                required
              />
            </p>
            <button type="submit" className="font-16px" disabled={sending}>
              <span>{sending ? "Entrando…" : "Entrar"}</span>
            </button>
            <button
              type="button"
              className="font-16px"
              onClick={() => {
                setError(null);
                setStep("email");
              }}
            >
              <span>Reenviar código</span>
            </button>
          </form>
        )}
      </section>
    </>
  );
}