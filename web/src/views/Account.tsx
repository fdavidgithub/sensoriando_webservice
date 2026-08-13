import { type FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError } from "../api/client";
import {
  type ProfileInput,
  linkThing,
  listPrivateThings,
  listSensorUnits,
  readPrivateAccount,
  savePreferredUnit,
  savePrivateAccount,
} from "../api/endpoints";
import type { ThingSensor } from "../api/types";
import ErrorBanner from "../components/ErrorBanner";
import Loading from "../components/Loading";
import { BRAZIL_STATES, COUNTRIES } from "../lib/locations";
import { type ChartType, readChartType, writeChartType } from "../lib/prefs";
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

// MAX_PRECISION as the running Django code defines it in users/views.py.
// base/constants.py carries a stale 5 that no view reads.
const PRECISIONS = [0, 1, 2];

function message(caught: unknown, fallback: string): string {
  return caught instanceof ApiError ? caught.message : fallback;
}

function ProfileTab() {
  const account = useApi(() => readPrivateAccount(), []);
  const [form, setForm] = useState<ProfileInput | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (account.data) {
      const { first_name, last_name, email, city, state, country } = account.data;
      setForm({ first_name, last_name, email, city, state, country });
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
      setError(message(caught, "Falha inesperada ao salvar o perfil"));
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
        <label className="font-16px" htmlFor="first_name">
          Nome
        </label>
        <input
          id="first_name"
          value={form.first_name}
          onChange={(event) => update("first_name", event.target.value)}
        />
      </p>
      <p>
        <label className="font-16px" htmlFor="last_name">
          Sobrenome
        </label>
        <input
          id="last_name"
          value={form.last_name}
          onChange={(event) => update("last_name", event.target.value)}
        />
      </p>
      <p>
        <label className="font-16px" htmlFor="email">
          E-mail
        </label>
        <input
          id="email"
          type="email"
          value={form.email}
          onChange={(event) => update("email", event.target.value)}
        />
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

      <button type="submit">Alterar</button>
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
      setError(message(caught, "Falha inesperada ao vincular a central"));
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
  const [error, setError] = useState<string | null>(null);
  const [unitId, setUnitId] = useState<number | null>(null);
  const [precision, setPrecision] = useState(PRECISIONS[0]);

  const sensorUnits = (units.data ?? []).filter((unit) => unit.id_sensor === sensor.id);

  // The chart type is presentation only, so it stays in localStorage. The unit
  // and the precision are moving to the database, where the API can apply them
  // before serving the value -- hence the PUT rather than a local write.
  async function persist(nextUnitId: number | null, nextPrecision: number) {
    if (nextUnitId === null) return;

    setError(null);
    try {
      await savePreferredUnit({
        id_sensor: sensor.id,
        id_unit: nextUnitId,
        precision: nextPrecision,
      });
    } catch (caught: unknown) {
      setError(message(caught, "Falha inesperada ao salvar a preferência"));
    }
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
              setUnitId(next);
              void persist(next, precision);
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

      <td>
        <select
          value={precision}
          onChange={(event) => {
            const next = Number(event.target.value);
            setPrecision(next);
            void persist(unitId, next);
          }}
        >
          {PRECISIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </td>

      <td>{error && <ErrorBanner message={error} />}</td>
    </tr>
  );
}

function SensorsTab() {
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
            <th>Precisão</th>
            <th />
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
