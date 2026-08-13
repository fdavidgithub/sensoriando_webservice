import { Link } from "react-router-dom";

import type { Thing } from "../api/types";
import type { FilterKey } from "../lib/filters";
import { countryName } from "../lib/country";

interface Props {
  thing: Thing;
  onFilter: (key: FilterKey, value: string) => void;
}

export default function ThingCard({ thing, onFilter }: Props) {
  return (
    <li>
      <div className="card-icon">
        <img src="/img/service-1.png" alt="Icon" />
      </div>

      <h3 className="font-22px">
        <Link to={`/thing/detail/${thing.uuid}`} className="underline-black__half">
          {thing.thing}
        </Link>
      </h3>

      <div className="font-13px card-body">
        <div className="column">
          <div>
            <b>Cidade</b>
          </div>
          <div>
            <b>Pais</b>
          </div>
          <div>
            <b>Sensores</b>
          </div>
          <div>
            <b>Tags</b>
          </div>
        </div>

        <div className="column">
          <div>
            <button
              type="button"
              className="underline-black"
              onClick={() => onFilter("city", thing.account.city)}
            >
              {thing.account.city}
            </button>
            {" / "}
            <button
              type="button"
              className="underline-black"
              onClick={() => onFilter("state", thing.account.state)}
            >
              {thing.account.state}
            </button>
          </div>

          <div>
            <button
              type="button"
              className="underline-black"
              onClick={() => onFilter("country", thing.account.country)}
            >
              {countryName(thing.account.country)}
            </button>
          </div>

          <div>
            {thing.sensors.map((sensor) => (
              <button
                key={sensor.id}
                type="button"
                className="underline-black"
                onClick={() => onFilter("sensor", sensor.name)}
              >
                {sensor.name}
              </button>
            ))}
          </div>

          <div>
            {thing.thingtags.map((tag) => (
              <button
                key={tag.id}
                type="button"
                className="underline-black"
                onClick={() => onFilter("thing_tag", tag.name)}
              >
                {tag.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="card-body">
        <div className="column">
          <div>
            <b className="font-13px">Última leitura</b>
          </div>
        </div>
        <div className="column">
          <div className="font-13px">{thing.lastupdate}</div>
        </div>
      </div>
    </li>
  );
}
