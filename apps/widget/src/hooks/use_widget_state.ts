import { Dispatch, SetStateAction, useCallback, useState } from "react";

export function useWidgetState<TState extends object>(
  defaults: TState,
): [TState, Dispatch<SetStateAction<TState>>] {
  const [state, setLocalState] = useState<TState>(() => {
    const hostState = window.openai?.widgetState;
    return isRecord(hostState) ? ({ ...defaults, ...hostState } as TState) : defaults;
  });

  const setState = useCallback<Dispatch<SetStateAction<TState>>>((next) => {
    setLocalState((current) => {
      const resolved = typeof next === "function" ? (next as (value: TState) => TState)(current) : next;
      window.openai?.setWidgetState?.(resolved);
      return resolved;
    });
  }, []);

  return [state, setState];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
