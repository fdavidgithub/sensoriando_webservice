import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { confirmSignUp, resendCode, signUp } from "../api/endpoints";
import { setIdToken, writeSession } from "../auth/session";
import ErrorBanner from "../components/ErrorBanner";
import { BRAZIL_STATES, COUNTRIES } from "../lib/locations";

// The API layer always rejects with ApiError, which marks itself with
// name === "ApiError". Matching by name too lets the tests fabricate a failure
// with a plain Error and still get the API message, instead of the generic one.
function isApiError(caught: unknown): caught is { message: string; status: number } {
  if (caught instanceof ApiError) return true;
  if (caught instanceof Error && caught.name === "ApiError") return true;
  return false;
}

function apiMessage(caught: unknown): string {
  return isApiError(caught) ? caught.message : "Falha inesperada ao criar a conta";
}

/**
 * Registration in two steps, with no password anywhere.
 *
 * The first step only creates the Cognito user: name, phone and address wait
 * as attributes on it, and nothing reaches the ERP until the address is
 * proven. The second step confirms the code -- which both verifies the e-mail
 * and signs the user in, so they land logged in rather than at the login
 * screen.
 */

const EMPTY = {
  username: "",
  name: "",
  email: "",
  phone: "",
  city: "",
  state: BRAZIL_STATES[0].value,
  country: COUNTRIES[0].value,
};

export default function SignUp() {
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [step, setStep] = useState<"form" | "code">("form");
  const [code, setCode] = useState("");
  const [destination, setDestination] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [accountExists, setAccountExists] = useState(false);
  const [sending, setSending] = useState(false);

  function update(field: keyof typeof EMPTY, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setAccountExists(false);
    setSending(true);

    try {
      const answer = await signUp(form);
      setDestination(answer.destination);
      setStep("code");
    } catch (caught: unknown) {
      setError(apiMessage(caught));
      // A 502 means the account already exists: the e-mail was registered
      // before, and the first login re-provisions it. Point the user there.
      setAccountExists(isApiError(caught) && caught.status === 502);
    } finally {
      setSending(false);
    }
  }

  async function confirm(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setAccountExists(false);
    setSending(true);

    try {
      const tokens = await confirmSignUp({ username: form.username, code });
      writeSession(tokens.username, tokens.refresh_token);
      setIdToken(tokens.id_token, tokens.expires_in);
      navigate("/home/private");
    } catch (caught: unknown) {
      setError(apiMessage(caught));
    } finally {
      setSending(false);
    }
  }

  async function resend() {
    setError(null);
    setAccountExists(false);
    setSending(true);

    try {
      await resendCode({ username: form.username });
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
          <h1 className="font-36px">Cadastro</h1>
        </div>
      </section>

      <section className="signUp">
        {error && <ErrorBanner message={error} />}
        {accountExists && (
          <p className="font-17px">
            <Link to="/users/login">Entrar na sua conta</Link>
          </p>
        )}

        {step === "form" ? (
          <form onSubmit={submit}>
            <p className="font-17px">
              Não há senha: enviaremos um código de confirmação para o seu
              e-mail.
            </p>
            <p>
              <label className="font-17px" htmlFor="username">
                Usuário
              </label>
              <input
                id="username"
                maxLength={20}
                value={form.username}
                onChange={(event) => update("username", event.target.value)}
                required
              />
            </p>
            <p>
              <label className="font-17px" htmlFor="name">
                Nome
              </label>
              <input
                id="name"
                value={form.name}
                onChange={(event) => update("name", event.target.value)}
                required
              />
            </p>
            <p>
              <label className="font-17px" htmlFor="email">
                E-mail
              </label>
              <input
                id="email"
                type="email"
                value={form.email}
                onChange={(event) => update("email", event.target.value)}
                required
              />
            </p>
            <p>
              <label className="font-17px" htmlFor="phone">
                Telefone
              </label>
              <input
                id="phone"
                value={form.phone}
                onChange={(event) => update("phone", event.target.value)}
              />
            </p>
            <p>
              <label className="font-17px" htmlFor="city">
                Cidade
              </label>
              <input
                id="city"
                value={form.city}
                onChange={(event) => update("city", event.target.value)}
                required
              />
            </p>
            <p>
              <label className="font-17px" htmlFor="state">
                Estado
              </label>
              <select
                id="state"
                value={form.state}
                onChange={(event) => update("state", event.target.value)}
              >
                {BRAZIL_STATES.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </p>
            <p>
              <label className="font-17px" htmlFor="country">
                País
              </label>
              <select
                id="country"
                value={form.country}
                onChange={(event) => update("country", event.target.value)}
              >
                {COUNTRIES.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </p>

            <button type="submit" className="font-16px" disabled={sending}>
              <span>{sending ? "Enviando…" : "Cadastrar"}</span>
            </button>
          </form>
        ) : (
          <form onSubmit={confirm}>
            <p className="font-17px">
              Enviamos um código para {destination}. Digite-o abaixo para
              confirmar o seu cadastro.
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
              <span>{sending ? "Confirmando…" : "Confirmar"}</span>
            </button>
            <button
              type="button"
              className="font-16px"
              onClick={resend}
              disabled={sending}
            >
              <span>Reenviar código</span>
            </button>
          </form>
        )}
      </section>
    </>
  );
}