export interface Sensor {
  id: number;
  name: string;
}

export interface SensorTag {
  name: string;
}

export interface Account {
  username: string | null;
  city: string;
  state: string;
  country: string;
}

export interface ThingSensor {
  id: number;
  name: string;
}

// The API serializes thing tags with the sensor serializer, so they carry an
// `id` alongside the name.
export interface ThingTag {
  id: number;
  name: string;
}

export interface Thing {
  thing: string;
  uuid: string;
  /** Already formatted by the API as "dd/mm/aaaa HH:MM:SS", or "---". */
  lastupdate: string;
  account: Account;
  sensors: ThingSensor[];
  thingtags: ThingTag[];
}

export interface Reading {
  dtread: string;
  value: number;
  message: string | null;
}

export interface Stats {
  user: string;
  plan: string;
  records: number;
  record_unit: string;
  retation_current: number;
  retation_full: number;
  retation_unit: string;
}

/** Served by GET /sensors/units, which does not exist yet. */
export interface SensorUnit {
  id: number;
  id_sensor: number;
  name: string;
  initial: string | null;
  precision: number | null;
  isdefault: boolean;
}
