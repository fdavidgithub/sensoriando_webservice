import type { Stats } from "../api/types";

interface Props {
  stats: Stats;
}

export default function StatsPanel({ stats }: Props) {
  return (
    <div className="col-pad">
      <h1 className="font-36px">Indicadores</h1>

      <div className="form-group font-17px">
        <div>
          <b>Plano:</b> {stats.plan}
        </div>
        <div>
          <b>Total de Registros:</b> {stats.records} {stats.record_unit}
        </div>
        <div>
          <b>Retenção:</b> {stats.retation_current} de {stats.retation_full}{" "}
          {stats.retation_unit}
        </div>
      </div>
    </div>
  );
}
