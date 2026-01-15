// /components/PartidosList.tsx
"use client";

import React from "react";
import Link from "next/link";
import MatchCard from "./MatchCard";
import EmptyState from "./EmptyState";
import type { PartidoListItem } from "../hooks/usePartidosList";

type PartidosListProps = {
  partidos: PartidoListItem[];
  dict: any;
  lang: string;
  loading?: boolean;
  error?: string | null;
};

export default function PartidosList({
  partidos,
  dict,
  lang,
  loading = false,
  error = null,
}: PartidosListProps) {
  if (loading) {
    return (
      <div className="w-full">
        <EmptyState dict={dict} type="general" variant="loading" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full">
        <EmptyState dict={dict} type="general" variant="error" />
      </div>
    );
  }

  if (!partidos || partidos.length === 0) {
    return (
      <div className="w-full">
        <EmptyState dict={dict} type="competicion" variant="no_data_generic" />
      </div>
    );
  }

  // Mapear partidos al formato de MatchCard
  const matches = partidos.map((p) => ({
    id: p.id,
    identificador_federacion: p.identificador_federacion,
    jornada: p.jornada_numero,
    jugado: p.jugado,
    fecha_hora: p.fecha_hora,
    pabellon: "", // No viene en la lista, se puede obtener del detalle
    arbitros: [], // No viene en la lista, se puede obtener del detalle
    local: {
      id: p.local.id,
      nombre: p.local.nombre,
      escudo: p.local.escudo,
      slug: p.local.slug,
      goles: p.goles_local,
    },
    visitante: {
      id: p.visitante.id,
      nombre: p.visitante.nombre,
      escudo: p.visitante.escudo,
      slug: p.visitante.slug,
      goles: p.goles_visitante,
    },
  }));

  return (
    <div className="w-full">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {matches.map((match) => (
          <MatchCard
            key={match.id}
            match={match}
            divisionLogoSrc=""
            dict={dict}
            lang={lang}
          />
        ))}
      </div>
    </div>
  );
}

