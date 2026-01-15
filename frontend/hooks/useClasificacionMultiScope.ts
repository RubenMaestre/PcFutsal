// /frontend/hooks/useClasificacionMultiScope.ts
"use client";

import React from "react";

// 👇 si estamos en el navegador usaremos rutas relativas
const isBrowser = typeof window !== "undefined";
const API_BASE = !isBrowser
  ? process.env.NEXT_PUBLIC_API_BASE_URL || "https://pcfutsal.es"
  : ""; // en browser → relativo

type Scope = "overall" | "home" | "away";

export function useClasificacionMultiScope(
  grupoId: number | null,
  jornada: number | null
) {
  const [dataByScope, setDataByScope] = React.useState<{
    overall: any | null;
    home: any | null;
    away: any | null;
  }>({
    overall: null,
    home: null,
    away: null,
  });

  const [loadingScope, setLoadingScope] = React.useState<Scope | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const buildUrl = React.useCallback(
    (scope: Scope, j: number | null | undefined) => {
      if (!grupoId) return "";
      // 👇 en cliente usamos relativo para evitar problemas de CORS / proxy
      if (isBrowser) {
        let url = `/api/estadisticas/clasificacion-completa/?grupo_id=${grupoId}&scope=${scope}`;
        if (typeof j === "number") {
          url += `&jornada=${j}`;
        }
        return url;
      }
      // 👇 en SSR usamos la base del .env
      let url = `${API_BASE}/api/estadisticas/clasificacion-completa/?grupo_id=${grupoId}&scope=${scope}`;
      if (typeof j === "number") {
        url += `&jornada=${j}`;
      }
      return url;
    },
    [grupoId]
  );

  const fetchScope = React.useCallback(
    async (scope: Scope, j?: number | null) => {
      if (!grupoId) return;
      const url = buildUrl(scope, j);
      if (!url) return;
      setLoadingScope(scope);
      try {
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const json = await res.json();
        setDataByScope((prev) => ({
          ...prev,
          [scope]: json,
        }));
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError("Error al cargar clasificación");
      } finally {
        setLoadingScope(null);
      }
    },
    [buildUrl, grupoId]
  );

  // 👇 pedir una jornada concreta sin tocar el resto
  const fetchSingleScope = React.useCallback(
    async (scope: Scope, j: number) => {
      if (!grupoId) return null;
      const url = buildUrl(scope, j);
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const json = await res.json();
      return json;
    },
    [buildUrl, grupoId]
  );

  // efecto inicial / cambio de grupo o jornada
  React.useEffect(() => {
    if (!grupoId) {
      setDataByScope({ overall: null, home: null, away: null });
      return;
    }
    fetchScope("overall", jornada || null);
    fetchScope("home", jornada || null);
    fetchScope("away", jornada || null);
  }, [grupoId, jornada, fetchScope]);

  return {
    dataByScope,
    loadingScope,
    error,
    fetchScope,
    fetchSingleScope,
  };
}
