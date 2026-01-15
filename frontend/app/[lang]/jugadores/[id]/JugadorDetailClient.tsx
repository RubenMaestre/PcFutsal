// /app/[lang]/jugadores/[id]/JugadorDetailClient.tsx
"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useJugadorFull } from "../../../../hooks/useJugadorFull";
import EmptyState from "../../../../components/EmptyState";
import JugadorReconocimientosCard from "../../../../components/JugadorReconocimientosCard";

type Lang = "es" | "val" | "en" | "fr" | "it" | "pt" | "de";

type Props = {
  lang: Lang;
  jugadorId: string;
  dict: any;
};

function Label({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-xs uppercase tracking-wide text-slate-300/80">
      {children}
    </span>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col">
      <Label>{label}</Label>
      <div className="text-white font-semibold mt-1">{value ?? "-"}</div>
    </div>
  );
}

export default function JugadorDetailClient({ lang, jugadorId, dict }: Props) {
  const router = useRouter();
  
  // jugadorId puede ser un número (ID) o un slug (string)
  const { data, loading, error } = useJugadorFull({
    jugadorId: jugadorId, // Acepta ID o slug
    include: ["valoraciones", "historial", "partidos", "stats"],
    enabled: !!jugadorId,
  });

  const L = dict?.jugador_detail || {};

  // Redirigir a slug si se accede con ID y el jugador tiene slug
  React.useEffect(() => {
    if (data?.jugador?.slug && jugadorId && jugadorId !== data.jugador.slug) {
      // Si el jugadorId es numérico (ID) y hay slug disponible, redirigir
      const isNumericId = /^\d+$/.test(String(jugadorId));
      if (isNumericId) {
        router.replace(`/${lang}/jugadores/${data.jugador.slug}`);
      }
    }
  }, [data?.jugador?.slug, jugadorId, lang, router]);

  if (loading) {
    return (
      <div className="px-4 md:px-8 py-6 text-slate-200 text-sm">
        {L.loading || "Cargando jugador..."}
      </div>
    );
  }

  if (error || !data?.jugador) {
    return (
      <div className="px-4 md:px-8 py-6">
        <EmptyState
          type="general"
          variant="error"
          customMessage={error || L.not_found || "Jugador no encontrado."}
          dict={dict}
        />
      </div>
    );
  }

  const jugador = data.jugador || {};
  const clubActual = data.club_actual;
  const temporadaActual = data.temporada_actual;
  const valoracion = data.valoraciones;
  const stats = data.stats_actuales;
  const historial = data.historial || [];
  const partidos = data.partidos;

  const nombre = jugador.nombre || jugador.apodo || (L.jugador_fallback || "Jugador");
  const apodo = jugador.apodo && jugador.apodo !== nombre ? jugador.apodo : null;
  const foto = jugador.foto_url || "";
  const posicion = jugador.posicion_principal || "";
  const edad = jugador.edad_display || jugador.edad_estimacion || null;
  const dorsal = data.dorsal_actual || null;

  return (
    <div className="px-4 md:px-8 py-6 space-y-6">
      {/* Header del jugador */}
      <div className="relative overflow-hidden rounded-2xl border border-white/10 p-6 md:p-8 bg-gradient-to-br from-brand-primary/20 to-black/40">
        <div className="relative flex flex-col md:flex-row md:items-center gap-6">
          {/* Foto */}
          {foto && (
            <div className="flex-shrink-0">
              <div className="w-24 h-24 md:w-32 md:h-32 rounded-xl overflow-hidden border-2 border-white/20 shadow-lg bg-white/5">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={foto}
                  alt={nombre}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          )}

          {/* Información principal */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h1 className="text-3xl md:text-4xl font-bold text-white">
                {nombre}
              </h1>
              {apodo && (
                <span className="px-2 py-1 rounded text-xs font-semibold bg-white/10 text-slate-300 border border-white/10">
                  {apodo}
                </span>
              )}
            </div>

            {/* Posición, edad, club */}
            <div className="flex flex-wrap items-center gap-4 mt-3">
              {posicion && (
                <Stat label={L.header?.posicion || "Posición"} value={posicion} />
              )}
              {edad && (
                <Stat label={L.header?.edad || "Edad"} value={`${edad} años`} />
              )}
              {dorsal && (
                <Stat label={L.header?.dorsal || "Dorsal"} value={dorsal} />
              )}
              {clubActual && (
                <div className="flex flex-col">
                  <Label>{L.header?.club_actual || "Club actual"}</Label>
                  <Link
                    href={`/${lang}/clubes/${clubActual.id}`}
                    className="text-white font-semibold mt-1 hover:text-brand-accent transition-colors flex items-center gap-2"
                  >
                    {clubActual.nombre_corto || clubActual.nombre}
                    {clubActual.escudo_url && (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={clubActual.escudo_url}
                        alt={clubActual.nombre}
                        className="w-6 h-6 object-contain"
                      />
                    )}
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Reconocimientos MVP y Fantasy */}
      {jugador.id && (
        <JugadorReconocimientosCard
          jugadorId={jugador.id}
          dict={dict}
          lang={lang}
        />
      )}

      {/* Tarjeta FIFA */}
      {valoracion && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">
            {L.fifa_card?.title || "Valoración FIFA"}
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="col-span-2 md:col-span-3">
              <div className="text-center p-4 bg-brand-primary/20 rounded-lg border border-brand-primary/30">
                <Label>{L.fifa_card?.media_global || "Media Global"}</Label>
                <div className="text-4xl font-bold text-white mt-2">
                  {valoracion.media_global?.toFixed(1) || "0.0"}
                </div>
                {valoracion.total_votos && (
                  <div className="text-xs text-slate-300 mt-1">
                    {L.fifa_card?.total_votos || "Votos"}: {valoracion.total_votos}
                  </div>
                )}
              </div>
            </div>
            {[
              { key: "ataque", label: L.fifa_card?.atributos?.ataque || "Ataque" },
              { key: "defensa", label: L.fifa_card?.atributos?.defensa || "Defensa" },
              { key: "pase", label: L.fifa_card?.atributos?.pase || "Pase" },
              { key: "regate", label: L.fifa_card?.atributos?.regate || "Regate" },
              { key: "potencia", label: L.fifa_card?.atributos?.potencia || "Potencia" },
              { key: "intensidad", label: L.fifa_card?.atributos?.intensidad || "Intensidad" },
              { key: "vision", label: L.fifa_card?.atributos?.vision || "Visión" },
              { key: "regularidad", label: L.fifa_card?.atributos?.regularidad || "Regularidad" },
              { key: "carisma", label: L.fifa_card?.atributos?.carisma || "Carisma" },
            ].map((attr) => (
              <div key={attr.key} className="flex flex-col">
                <Label>{attr.label}</Label>
                <div className="text-white font-semibold mt-1">
                  {(valoracion as any)[attr.key] || 0}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Estadísticas actuales - Temporada actual */}
      {stats && temporadaActual && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">
            {L.stats?.title || "Estadísticas actuales"}
            {temporadaActual?.nombre && (
              <span className="text-sm font-normal text-white/60 ml-2">
                ({temporadaActual.nombre})
              </span>
            )}
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Stat
              label={L.stats?.partidos_jugados || "Partidos jugados"}
              value={stats.partidos_jugados || 0}
            />
            <Stat
              label={L.stats?.goles || "Goles"}
              value={stats.goles || 0}
            />
            <Stat
              label={L.stats?.tarjetas_amarillas || "Tarjetas amarillas"}
              value={stats.tarjetas_amarillas || 0}
            />
            <Stat
              label={L.stats?.tarjetas_rojas || "Tarjetas rojas"}
              value={stats.tarjetas_rojas || 0}
            />
          </div>
        </div>
      )}

      {/* Historial */}
      {historial.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">
            {L.historial?.title || "Historial"}
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 px-3 text-slate-300">
                    {L.historial?.temporada || "Temporada"}
                  </th>
                  <th className="text-left py-2 px-3 text-slate-300">
                    {L.historial?.competicion || "Competición"}
                  </th>
                  <th className="text-left py-2 px-3 text-slate-300">
                    {L.historial?.club || "Club"}
                  </th>
                  <th className="text-center py-2 px-3 text-slate-300">
                    {L.historial?.partidos || "PJ"}
                  </th>
                  <th className="text-center py-2 px-3 text-slate-300">
                    {L.historial?.goles || "Goles"}
                  </th>
                </tr>
              </thead>
              <tbody>
                {historial.slice(0, 10).map((h: any, idx: number) => (
                  <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-2 px-3 text-white">{h.temporada}</td>
                    <td className="py-2 px-3 text-slate-300">
                      {h.competicion} {h.grupo && `· ${h.grupo}`}
                    </td>
                    <td className="py-2 px-3 text-white">
                      {h.club_slug ? (
                        <Link
                          href={`/${lang}/clubes/${h.club_id || h.club_slug}`}
                          className="hover:text-brand-accent transition-colors"
                        >
                          {h.club_nombre || h.club}
                        </Link>
                      ) : (
                        h.club_nombre || h.club
                      )}
                    </td>
                    <td className="py-2 px-3 text-white text-center">{h.partidos_jugados || 0}</td>
                    <td className="py-2 px-3 text-white text-center">{h.goles || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Partidos recientes */}
      {partidos && partidos.partidos && partidos.partidos.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">
            {L.partidos?.title || "Partidos recientes"}
          </h2>
          <div className="space-y-3 mb-4">
            {partidos.partidos.slice(0, 5).map((p: any) => (
              <div
                key={p.partido_id}
                className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10"
              >
                <div className="flex-1">
                  <div className="text-white font-semibold">
                    {p.local} vs {p.visitante}
                  </div>
                  <div className="text-sm text-slate-300 mt-1">
                    {L.partidos?.jornada || "Jornada"} {p.jornada}
                    {p.fecha && ` · ${p.fecha}`}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-white font-bold">
                    {p.goles_local} - {p.goles_visitante}
                  </div>
                  {p.goles_jugador > 0 && (
                    <div className="text-xs text-brand-accent mt-1">
                      {p.goles_jugador} {L.partidos?.goles_jugador || "goles"}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          {partidos.totales && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 pt-4 border-t border-white/10">
              <Stat
                label={L.partidos?.totales?.partidos_jugados || "Partidos jugados"}
                value={partidos.totales.partidos_jugados || 0}
              />
              <Stat
                label={L.partidos?.totales?.goles || "Goles"}
                value={partidos.totales.goles || 0}
              />
              <Stat
                label={L.partidos?.totales?.mvps || "MVPs"}
                value={partidos.totales.mvps || 0}
              />
            </div>
          )}
        </div>
      )}

      {/* Botones de acción */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button className="px-6 py-3 bg-brand-primary text-white rounded-lg font-semibold hover:bg-brand-primary/90 transition-colors">
          {L.botones?.votar || "Votar"}
        </button>
        <button className="px-6 py-3 bg-white/10 text-white rounded-lg font-semibold hover:bg-white/20 transition-colors border border-white/20">
          {L.botones?.verificar_perfil || "¿Eres tú? Verifica el perfil"}
        </button>
      </div>
    </div>
  );
}
