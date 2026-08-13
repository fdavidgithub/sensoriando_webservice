import { useCallback, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { listPublicThings, listSensorTags, listSensors } from "../api/endpoints";
import EmptyState from "../components/EmptyState";
import ErrorBanner from "../components/ErrorBanner";
import FilterDialog from "../components/FilterDialog";
import Loading from "../components/Loading";
import ThingCard from "../components/ThingCard";
import { useApi } from "../lib/useApi";
import {
  type FilterKey,
  type Filters,
  filtersFromSearch,
  searchFromFilters,
} from "../lib/filters";

export default function PublicHome() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [dialogOpen, setDialogOpen] = useState(false);

  const search = searchParams.toString();
  const filters = useMemo(() => filtersFromSearch(search), [search]);

  const things = useApi(() => listPublicThings(filters), [search]);
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
          <h1 className="font-36px">Dispositivos</h1>
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
