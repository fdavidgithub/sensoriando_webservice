import { useEffect, useState } from "react";

import type { Sensor, SensorTag } from "../api/types";
import type { Filters } from "../lib/filters";

interface Props {
  open: boolean;
  sensors: Sensor[];
  tags: SensorTag[];
  filters: Filters;
  onApply: (filters: Filters) => void;
  onClear: () => void;
  onClose: () => void;
}

export default function FilterDialog({
  open,
  sensors,
  tags,
  filters,
  onApply,
  onClear,
  onClose,
}: Props) {
  const [sensor, setSensor] = useState(filters.sensor ?? "");
  const [sensorTag, setSensorTag] = useState(filters.sensor_tag ?? "");

  // The dialog stays mounted (only hidden) so its selects can hold draft
  // state, but that means the initial useState above only ever runs once. A
  // filter picked from a card (e.g. clicking a sensor name) changes `filters`
  // without this component remounting, so the selects must resync whenever
  // the dialog is reopened -- otherwise they show stale values and pressing
  // Aplicar would revert the very filter that was just clicked.
  useEffect(() => {
    if (open) {
      setSensor(filters.sensor ?? "");
      setSensorTag(filters.sensor_tag ?? "");
    }
  }, [open, filters.sensor, filters.sensor_tag]);

  if (!open) return null;

  function apply() {
    // Merge onto the full filter set: this dialog only edits sensor and
    // sensor_tag, so city/state/country/thing/thing_tag (set by clicking a
    // card) must survive an Aplicar click instead of being dropped.
    onApply({ ...filters, sensor, sensor_tag: sensorTag });
  }

  function clear() {
    setSensor("");
    setSensorTag("");
    onClear();
  }

  return (
    <dialog id="filter" open>
      <div className="dialog-container">
        <div className="modal-header">
          <h5 className="modal-title font-22px">Filtros</h5>
          <button type="button" onClick={onClose}>
            X
          </button>
        </div>

        <div>
          <select
            className="font-13px"
            value={sensor}
            onChange={(event) => setSensor(event.target.value)}
          >
            <option value="">Todos sensores</option>
            {sensors.map((item) => (
              <option key={item.id} value={item.name}>
                {item.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <select
            className="font-13px"
            value={sensorTag}
            onChange={(event) => setSensorTag(event.target.value)}
          >
            <option value="">Todas tags</option>
            {tags.map((item) => (
              <option key={item.name} value={item.name}>
                {item.name}
              </option>
            ))}
          </select>
        </div>

        <div className="modal-button-div">
          <button type="button" className="btn btn-primary btn-sm font-13px" onClick={apply}>
            Aplicar
          </button>
          <button type="button" className="btn btn-primary btn-sm font-13px" onClick={clear}>
            Limpar
          </button>
        </div>
      </div>
    </dialog>
  );
}
