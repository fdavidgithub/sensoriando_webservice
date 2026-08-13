import { useEffect, useState } from "react";

import { ApiError } from "../api/client";

interface State<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(call: () => Promise<T>, deps: unknown[]): State<T> {
  const [state, setState] = useState<State<T>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let active = true;
    setState({ data: null, loading: true, error: null });

    call()
      .then((data) => {
        if (active) setState({ data, loading: false, error: null });
      })
      .catch((error: unknown) => {
        if (!active) return;
        const message =
          error instanceof ApiError ? error.message : "Falha inesperada ao ler a API";
        setState({ data: null, loading: false, error: message });
      });

    return () => {
      // The view may unmount (or the filters may change) before the request
      // settles; without this the late answer would overwrite fresher state.
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
