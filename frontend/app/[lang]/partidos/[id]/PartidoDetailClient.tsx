// /app/[lang]/partidos/[id]/PartidoDetailClient.tsx
"use client";

import React from "react";
import { usePartidoDetalle } from "../../../../hooks/usePartidoDetalle";
import { useJugadoresJornada } from "../../../../hooks/useJugadoresJornada";
import { useEquipoJornada } from "../../../../hooks/useEquipoJornada";
import PartidoHeader from "../../../../components/PartidoHeader";
import MVPPartidoCard from "../../../../components/MVPPartidoCard";
import PartidoTimeline from "../../../../components/PartidoTimeline";
import PartidoAlineaciones from "../../../../components/PartidoAlineaciones";
import PartidoStaff from "../../../../components/PartidoStaff";
import PartidoEstadisticas from "../../../../components/PartidoEstadisticas";
import EmptyState from "../../../../components/EmptyState";

type PartidoDetailClientProps = {
  partidoId: string | number;
  dict: any;
  lang: string;
};

export default function PartidoDetailClient({
  partidoId,
  dict,
  lang,
}: PartidoDetailClientProps) {
  const { data: partidoData, loading, error } = usePartidoDetalle(
    partidoId,
    null
  );

  // Obtener puntos de jugadores y equipos si tenemos grupo y jornada
  const grupoId = partidoData?.partido?.grupo?.id || null;
  const jornada = partidoData?.partido?.jornada_numero || null;

  const { data: valoracionesJugadores } = useJugadoresJornada(
    grupoId,
    jornada
  );

  const { data: valoracionesEquipos } = useEquipoJornada(grupoId, jornada);

  // Crear lookup de puntos por jugador_id
  const puntosPorJugador = React.useMemo(() => {
    if (!valoracionesJugadores?.ranking_jugadores) return {};
    const lookup: Record<number, number> = {};
    valoracionesJugadores.ranking_jugadores.forEach((j: any) => {
      lookup[j.jugador_id] = j.puntos;
    });
    return lookup;
  }, [valoracionesJugadores]);

  // Crear lookup de puntos por club_id
  const puntosPorEquipo = React.useMemo(() => {
    if (!valoracionesEquipos?.ranking_clubes) return {};
    const lookup: Record<number, number> = {};
    valoracionesEquipos.ranking_clubes.forEach((c: any) => {
      lookup[c.club_id] = c.score;
    });
    return lookup;
  }, [valoracionesEquipos]);

  if (loading) {
    return (
      <div className="w-full max-w-7xl mx-auto px-4 py-6">
        <EmptyState dict={dict} type="general" variant="loading" />
      </div>
    );
  }

  if (error || !partidoData) {
    return (
      <div className="w-full max-w-7xl mx-auto px-4 py-6">
        <EmptyState dict={dict} type="general" variant="error" />
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-6 space-y-6">
      <PartidoHeader
        partido={partidoData.partido}
        arbitros={partidoData.arbitros}
        puntosEquipos={puntosPorEquipo}
        dict={dict}
        lang={lang}
      />

      {/* MVP del Partido */}
      {partidoData.partido.id && (
        <MVPPartidoCard
          partidoId={partidoData.partido.id}
          dict={dict}
          lang={lang}
        />
      )}

      <PartidoTimeline
        eventos={partidoData.eventos}
        local={partidoData.partido.local}
        visitante={partidoData.partido.visitante}
        dict={dict}
        lang={lang}
      />

      <PartidoAlineaciones
        alineaciones={partidoData.alineaciones}
        puntosJugadores={puntosPorJugador}
        dict={dict}
        lang={lang}
      />

      <PartidoStaff
        staff={partidoData.alineaciones}
        dict={dict}
        lang={lang}
      />

      <PartidoEstadisticas
        estadisticas={partidoData.estadisticas}
        dict={dict}
        lang={lang}
      />
    </div>
  );
}




