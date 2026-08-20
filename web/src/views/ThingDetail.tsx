import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import type { Period } from "../api/endpoints";
import {
  listPrivateThings,
  listPublicThings,
  readPrivateDetail,
  readPublicDetail,
} from "../api/endpoints";
import { readSession } from "../auth/session";
import EmptyState from "../components/EmptyState";
import ErrorBanner from "../components/ErrorBanner";
import Loading from "../components/Loading";
import SensorChart from "../components/SensorChart";
import { chartLabel, chartLegend } from "../lib/format";
import { readChartType, readPeriod, writePeriod } from "../lib/prefs";
import { useApi } from "../lib/useApi";

const PERIOD_LABELS: Array<{ value: Period; text: string }> = [
  { value: "second", text: "Segundos" },
  { value: "minute", text: "Minutos" },
  { value: "hour", text: "Horas" },
  { value: "day", text: "Dias" },
  { value: "month", text: "Meses" },
  { value: "year", text: "Anos" },
];

function SensorPanel({
  uuid,
  sensorId,
  sensorName,
  period,
  isPublic,
}: {
  uuid: string;
  sensorId: number;
  sensorName: string;
  period: Period;
  isPublic: boolean;
}) {
  const readings = useApi(
    () =>
      (isPublic ? readPublicDetail : readPrivateDetail)({
        thing: uuid,
        sensor: sensorName,
        period,
      }),
    [uuid, sensorName, period, isPublic],
  );

  const type = readChartType(sensorId);

  const points = useMemo(
    () =>
      (readings.data ?? []).map((reading) => ({
        legend: chartLegend(period, new Date(reading.dtread)),
        value: reading.value,
      })),
    [readings.data, period],
  );

  const label = useMemo(() => {
    const last = readings.data?.at(-1);
    return last ? chartLabel(period, new Date(last.dtread)) : "";
  }, [readings.data, period]);

  return (
    <li>
      <div>
        <b>{sensorName}</b>
      </div>

      <div>
        {readings.loading && <Loading />}
        {readings.error && <ErrorBanner message={readings.error} />}
        {readings.data?.length === 0 && <EmptyState message="Não há leituras para exibir." />}

        {points.length > 0 && type === "table" && (
          <table className="table table-striped" width="100%">
            <thead>
              <tr>
                <th>Data</th>
                <th>Mensagem</th>
              </tr>
            </thead>
            <tbody>
              {readings.data?.map((reading, index) => (
                <tr key={`${reading.dtread}-${index}`}>
                  <th>{reading.dtread}</th>
                  <th>{reading.message}</th>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {points.length > 0 && type === "display" && (
          <table className="table table-striped" width="100%">
            <tbody>
              <tr>
                <th>
                  <font size="20">{points.at(-1)?.value}</font>
                </th>
              </tr>
            </tbody>
          </table>
        )}

        {points.length > 0 && type !== "table" && type !== "display" && (
          <SensorChart points={points} label={label} type={type} />
        )}
      </div>
    </li>
  );
}

export default function ThingDetail() {
  const { uuid = "" } = useParams();
  const [period, setPeriod] = useState<Period>(readPeriod());

  // The route carries only the uuid, so the sensor names come from the thing
  // listings. Which listing the uuid turns up in is also what says whether the
  // readings come from the public or the private endpoint.
  const hasSession = Boolean(readSession());
  const publicThings = useApi(() => listPublicThings(), []);
  const privateThings = useApi(
    () => (hasSession ? listPrivateThings() : Promise.resolve([])),
    [hasSession],
  );

  const publicThing = publicThings.data?.find((candidate) => candidate.uuid === uuid);
  const privateThing = privateThings.data?.find((candidate) => candidate.uuid === uuid);
  const thing = publicThing ?? privateThing;
  const isPublic = Boolean(publicThing);

  const loading = publicThings.loading || privateThings.loading;
  // This route is public: a visitor who never authenticates must be able to
  // read it. The private listing only enriches the page for a signed-in owner,
  // so its failure -- including a stale session rejected by the API -- is
  // never shown here. Only the public listing, which every visitor depends on,
  // can produce the page-level error.
  const error = publicThings.error;
  const privateSettled = Boolean(privateThings.data) || Boolean(privateThings.error);
  const settled = Boolean(publicThings.data) && privateSettled;

  function choosePeriod(next: Period) {
    writePeriod(next);
    setPeriod(next);
  }

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">{thing?.thing ?? "Dispositivo"}</h1>

          <div className="home-button-list">
            <div className="home-dropdown">
              <button className="font-16px" type="button">
                Visualizar dados
              </button>
              <div className="home-dropdown-content">
                {PERIOD_LABELS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    className="font-13px underline-white"
                    onClick={() => choosePeriod(option.value)}
                  >
                    {option.text}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="charts">
        {loading && <Loading />}
        {error && <ErrorBanner message={error} />}
        {settled && !thing && <EmptyState message="Dispositivo não encontrado." />}

        {thing && (
          <ul>
            {thing.sensors.map((sensor) => (
              <SensorPanel
                key={sensor.id}
                uuid={uuid}
                sensorId={sensor.id}
                sensorName={sensor.name}
                period={period}
                isPublic={isPublic}
              />
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
