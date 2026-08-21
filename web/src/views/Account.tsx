import { type FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError } from "../api/client";
import {
  type ProfileInput,
  linkThing,
  listPrivateThings,
  listSensorUnits,
  readPrivateAccount,
  savePrivateAccount,
} from "../api/endpoints";
import type { ThingSensor } from "../api/types";
import ErrorBanner from "../components/ErrorBanner";
import Loading from "../components/Loading";
import { BRAZIL_STATES, COUNTRIES } from "../lib/locations";
import {
  type ChartType,
  readChartType,
  readPreferredUnit,
  writeChartType,
  writePreferredUnit,
} from "../lib/prefs";
import { useApi } from "../lib/useApi";

const TABS = [
  { id: "profile", label: "Perfil" },
  { id: "things", label: "Centrais" },
  { id: "sensors", label: "Sensores" },
] as const;

const CHART_TYPES: Array<{ value: ChartType; label: string }> = [
  { value: "line", label: "Linha" },
  { value: "bar", label: "Barra" },
  { value: "table", label: "Tabela" },
  { value: "display", label: "Display" },
];

// The API layer always rejects with ApiError, which marks itself with
// name === "ApiError". Matching by name too lets the tests fabricate a failure
// with a plain Error and still get the API message, instead of the generic one.
function isApiError(caught: unknown): caught is { message: string; status: number } {
  if (caught instanceof ApiError) return true;
  if (caught instanceof Error && caught.name === "ApiError") return true;
  return false;
}

function message(caught: unknown, fallback: string): string {
  return isApiError(caught) ? caught.message : fallback;
}

function ProfileTab() {
  const account = useApi(() => readPrivateAccount(), []);
  const [form, setForm] = useState<ProfileInput | null>(null);
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (account.data) {
      const { name, phone, city, state, country } = account.data;
      setForm({ name, phone, city, state, country });
      setEmail(account.data.email);
    }
  }, [account.data]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!form) return;

    setError(null);
    setSaved(false);
    try {
      await savePrivateAccount(form);
      setSaved(true);
    } catch (caught: unknown) {
      if (isApiError(caught) && caught.status === 409) {
        setError("Conta ainda não registrada. Entre novamente para concluir o cadastro.");
      } else {
        setError(message(caught, "Falha inesperada ao salvar o perfil"));
      }
    }
  }

  function update(field: keyof ProfileInput, value: string) {
    setForm((current) => (current ? { ...current, [field]: value } : current));
  }

  if (account.loading) return <Loading />;
  if (account.error) return <ErrorBanner message={account.error} />;
  if (!form) return null;

  return (
    <form onSubmit={submit}>
      {error && <ErrorBanner message={error} />}
      {saved && <p className="font-17px">Perfil salvo.</p>}

      <p>
        <label className="font-16px" htmlFor="name">
          Nome
        </label>
        <input
          id="name"
          value={form.name}
          onChange={(event) => update("name", event.target.value)}
        />
      </p>
      <p>
        <label className="font-16px" htmlFor="phone">
          Telefone
        </label>
        <input
          id="phone"
          value={form.phone ?? ""}
          onChange={(event) => update("phone", event.target.value)}
        />
      </p>
      <p>
        <label className="font-16px" htmlFor="email">
          E-mail
        </label>
        <input id="email" type="email" value={email} readOnly />
      </p>
      <p>
        <label className="font-16px" htmlFor="city">
          Cidade
        </label>
        <input
          id="city"
          value={form.city}
          onChange={(event) => update("city", event.target.value)}
        />
      </p>
      <p>
        <label className="font-16px" htmlFor="state">
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
        <label className="font-16px" htmlFor="country">
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

      <button type="submit">Salvar</button>
    </form>
  );
}

function ThingsTab() {
  const things = useApi(() => listPrivateThings(), []);
  const [uuid, setUuid] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    try {
      await linkThing({ uuid });
      setUuid("");
    } catch (caught: unknown) {
      if (isApiError(caught)) {
        if (caught.status === 404) setError("Central não encontrada.");
        else if (caught.status === 409) setError("Esta central já pertence a uma conta.");
        else setError(caught.message);
      } else {
        setError("Falha inesperada ao vincular a central");
      }
    }
  }

  return (
    <>
      <form onSubmit={submit}>
        {error && <ErrorBanner message={error} />}
        <p>
          <label className="font-16px" htmlFor="uuid">
            Nova central
          </label>
          <input
            id="uuid"
            value={uuid}
            onChange={(event) => setUuid(event.target.value)}
            placeholder="UUID"
            required
          />
        </p>
        <button type="submit">Adicionar</button>
      </form>

      {things.loading && <Loading />}
      {things.error && <ErrorBanner message={things.error} />}
      {things.data && (
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Central</th>
              <th>UUID</th>
            </tr>
          </thead>
          <tbody>
            {things.data.map((thing) => (
              <tr key={thing.uuid}>
                <td>{thing.thing}</td>
                <td>{thing.uuid}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}

function SensorRow({ sensor }: { sensor: ThingSensor; }) {
  const units = useApi(() => listSensorUnits(), []);
  const [unitId, setUnitId] = useState<number | null>(() => readPreferredUnit(sensor.id));

  const sensorUnits = (units.data ?? []).filter((unit) => unit.id_sensor === sensor.id);

  // The chart type is presentation only, so it stays in localStorage. The unit
  // is a browser preference too, so both sit beside the period in prefs.ts.
  function selectUnit(next: number | null) {
    setUnitId(next);
    if (next !== null) writePreferredUnit(sensor.id, next);
  }

  return (
    <tr>
      <td>{sensor.name}</td>

      <td>
        <select
          defaultValue={readChartType(sensor.id)}
          onChange={(event) => writeChartType(sensor.id, event.target.value as ChartType)}
        >
          {CHART_TYPES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </td>

      <td>
        {units.error ? (
          <span className="font-13px">{units.error}</span>
        ) : (
          <select
            disabled={sensorUnits.length === 0}
            value={unitId ?? ""}
            onChange={(event) => {
              // Number("") is 0, not NaN -- the "—" placeholder must clear the
              // selection, not silently pick unit id 0.
              const raw = event.target.value;
              const next = raw === "" ? null : Number(raw);
              selectUnit(next);
            }}
          >
            <option value="">—</option>
            {sensorUnits.map((unit) => (
              <option key={unit.id} value={unit.id}>
                {unit.name}
              </option>
            ))}
          </select>
        )}
      </td>
    </tr>
  );
}

function SensorsTab() {
  // The unit is a browser preference, not an account setting: there is no table
  // in the schema linking an account to a unit. See lib/prefs.ts.
  const things = useApi(() => listPrivateThings(), []);

  // One row per distinct sensor across the account's things.
  const sensors = Array.from(
    new Map(
      (things.data ?? []).flatMap((thing) =>
        thing.sensors.map((sensor) => [sensor.id, sensor] as const),
      ),
    ).values(),
  );

  return (
    <>
      {things.loading && <Loading />}
      {things.error && <ErrorBanner message={things.error} />}

      <table className="table table-striped">
        <thead>
          <tr>
            <th>Sensor</th>
            <th>Gráfico</th>
            <th>Unidade</th>
          </tr>
        </thead>
        <tbody>
          {sensors.map((sensor) => (
            <SensorRow key={sensor.id} sensor={sensor} />
          ))}
        </tbody>
      </table>
    </>
  );
}

export default function Account() {
  const { username = "", tab = "profile" } = useParams();
  const active = TABS.some((candidate) => candidate.id === tab) ? tab : "profile";

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">Minha conta</h1>
        </div>
      </section>

      <section className="cards">
        <ul className="nav nav-tabs">
          {TABS.map((candidate) => (
            <li key={candidate.id} className={active === candidate.id ? "active" : ""}>
              <Link className="nav-link" to={`/users/account/${username}/${candidate.id}`}>
                {candidate.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="tab-content">
          {active === "profile" && <ProfileTab />}
          {active === "things" && <ThingsTab />}
          {active === "sensors" && <SensorsTab />}
        </div>
      </section>
    </>
  );
}
