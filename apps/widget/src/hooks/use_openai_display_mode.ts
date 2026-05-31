import { useEffect, useState } from "react";
import type { DisplayMode } from "../types.js";

type OpenAiGlobalsEvent = CustomEvent<{
  globals?: {
    displayMode?: DisplayMode;
  };
}>;

export function useOpenAiDisplayMode(): DisplayMode | undefined {
  const [displayMode, setDisplayMode] = useState<DisplayMode | undefined>(() => window.openai?.displayMode);

  useEffect(() => {
    function onSetGlobals(event: Event) {
      const globals = (event as OpenAiGlobalsEvent).detail?.globals;
      if (globals && "displayMode" in globals) {
        setDisplayMode(globals.displayMode);
      }
    }

    window.addEventListener("openai:set_globals", onSetGlobals);
    return () => window.removeEventListener("openai:set_globals", onSetGlobals);
  }, []);

  return displayMode;
}
