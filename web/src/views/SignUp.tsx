import { type FormEvent, useState } from "react";

import { ApiError } from "../api/client";
import { createAccount } from "../api/endpoints";
import ErrorBanner from "../components/ErrorBanner";
import { BRAZIL_STATES, COUNTRIES } from "../lib/locations";

const EMPTY = {
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  city: "",
  state: BRAZIL_STATES[0].value,
  country: COUNTRIES[0].value,
};

export default function SignUp() {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [sending, setSending] = useState(false);

  function update(field: keyof typeof EMPTY, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSending(true);

    try {
      await createAccount(form);
      setDone(true);
    } catch (caught: unknown) {
      setError(
        caught instanceof ApiError ? caught.message : "Falha inesperada ao criar a conta",
      );
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
        {done && <p className="font-17px">Conta criada.</p>}

        <form onSubmit={submit}>
          <p>
            <label className="font-17px" htmlFor="username">
              Usuário
            </label>
            <input
              id="username"
              value={form.username}
              onChange={(event) => update("username", event.target.value)}
              required
            />
          </p>
          <p>
            <label className="font-17px" htmlFor="first_name">
              Nome
            </label>
            <input
              id="first_name"
              value={form.first_name}
              onChange={(event) => update("first_name", event.target.value)}
              required
            />
          </p>
          <p>
            <label className="font-17px" htmlFor="last_name">
              Sobrenome
            </label>
            <input
              id="last_name"
              value={form.last_name}
              onChange={(event) => update("last_name", event.target.value)}
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
            <label className="font-17px" htmlFor="password">
              Senha
            </label>
            <input
              id="password"
              type="password"
              value={form.password}
              onChange={(event) => update("password", event.target.value)}
              required
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
      </section>
    </>
  );
}
