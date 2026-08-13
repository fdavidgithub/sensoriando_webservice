import { useCallback, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { listPrivateThings, listSensorTags, listSensors, readPrivateStats } from "../api/endpoints";
import EmptyState from "../components/EmptyState";
import ErrorBanner from "../components/ErrorBanner";
import FilterDialog from "../components/FilterDialog";
import Loading from "../components/Loading";
import StatsPanel from "../components/StatsPanel";
import ThingCard from "../components/ThingCard";
import {
  type FilterKey,
  type Filters,
  filtersFromSearch,
  searchFromFilters,
} from "../lib/filters";
import { useApi } from "../lib/useApi";

export default function PrivateHome() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [dialogOpen, setDialogOpen] = useState(false);

  const search = searchParams.toString();
  const filters = useMemo(() => filtersFromSearch(search), [search]);

  const things = useApi(() => listPrivateThings(filters), [search]);
  const stats = useApi(() => readPrivateStats(), []);
  const sensors = useApi(() => listSensors(), []);
  const tags = useApi(() => listSensorTags(), []);

  const applyFilters = useCallback(
    (next: Filters) => {
      setSearchParams(new URLSearchParams(searchFromFilters(next)));
      setDialogOpen(false);
    },
    [setSearchParams],
  );

  const addFilter = useCallback(
    (key: FilterKey, value: string) => applyFilters({ ...filters, [key]: value }),
    [applyFilters, filters],
  );

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">Meus dispositivos</h1>
          <button className="font-16px" type="button" onClick={() => setDialogOpen(true)}>
            Filtros
          </button>
        </div>
      </section>

      <section className="cards">
        {things.loading && <Loading />}
        {things.error && <ErrorBanner message={things.error} />}
        {things.data?.length === 0 && <EmptyState />}
        {things.data && things.data.length > 0 && (
          <ul>
            {things.data.map((thing) => (
              <ThingCard key={thing.uuid} thing={thing} onFilter={addFilter} />
            ))}
          </ul>
        )}
      </section>

      <section className="home">
        {stats.error && <ErrorBanner message={stats.error} />}
        {stats.data && <StatsPanel stats={stats.data} />}
      </section>

      <FilterDialog
        open={dialogOpen}
        sensors={sensors.data ?? []}
        tags={tags.data ?? []}
        filters={filters}
        onApply={applyFilters}
        onClear={() => applyFilters({})}
        onClose={() => setDialogOpen(false)}
      />
    </>
  );
}
