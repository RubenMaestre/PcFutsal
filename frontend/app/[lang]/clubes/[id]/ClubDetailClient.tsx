// /app/[lang]/clubes/[id]/ClubDetailClient.tsx
"use client";

import React from "react";
import Link from "next/link";
import { useClubHistorico } from "../../../../hooks/useClubHistorico";
import EquipoReconocimientosCard from "../../../../components/EquipoReconocimientosCard";

type Lang = "es" | "val" | "en" | "fr" | "it" | "pt" | "de";

type Props = {
  lang: Lang;
  clubId: string;
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

// Componente para el histórico de temporadas
function HistoricoTemporadas({ clubId, tempActual, dict }: { clubId: string; tempActual?: string; dict?: any }) {
  const { data, loading, error } = useClubHistorico(clubId);
  const H = dict?.club_detail?.historical || {};

  // Filtrar y ordenar histórico (excluir temporada actual, ordenar de más reciente a más antigua)
  const historicoFiltrado = React.useMemo(() => {
    if (!data?.historico || !Array.isArray(data.historico)) {
      return [];
    }

    return data.historico
      .filter((item) => {
        // Excluir temporada actual
        if (tempActual && item.temporada.trim() === tempActual.trim()) {
          return false;
        }
        return true;
      })
      .sort((a, b) => {
        // Ordenar por temporada descendente (más reciente primero)
        // Extraer año de la temporada (formato: "2024/2025")
        const getYear = (temp: string) => {
          const match = temp.match(/(\d{4})/);
          return match ? parseInt(match[1]) : 0;
        };
        return getYear(b.temporada) - getYear(a.temporada);
      });
  }, [data?.historico, tempActual]);

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-3">
      <h2 className="text-lg font-semibold text-white border-b border-white/10 pb-2">
        {dict?.club_detail?.historical_title || "Histórico de temporadas"}
      </h2>

      {loading && (
        <div className="text-slate-400 text-sm py-4 text-center">
          {H.loading || "Cargando histórico..."}
        </div>
      )}

      {error && (
        <div className="text-red-400 text-sm py-4 text-center">
          {H.error || "Error al cargar el histórico"}: {error}
        </div>
      )}

      {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-2 px-3 text-sm font-semibold text-slate-300">
                  {H.col_temporadas || "TEMPORADAS"}
                </th>
                <th className="text-left py-2 px-3 text-sm font-semibold text-slate-300">
                  {H.col_division || "DIVISIÓN"}
                </th>
                <th className="text-center py-2 px-3 text-sm font-semibold text-slate-300">
                  {H.col_posicion || "POSICIÓN"}
                </th>
                <th className="text-center py-2 px-3 text-sm font-semibold text-slate-300">
                  {H.col_puntos || "PUNTOS"}
                </th>
              </tr>
            </thead>
            <tbody>
              {historicoFiltrado.length > 0 ? (
                historicoFiltrado.map((item, idx) => (
                  <tr
                    key={idx}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >
                    {/* Columna TEMPORADAS */}
                    <td className="py-3 px-3">
                      <div className="text-white font-semibold text-sm">
                        {item.temporada || "—"}
                      </div>
                    </td>
                    
                    {/* Columna DIVISIÓN */}
                    <td className="py-3 px-3">
                      <div className="text-slate-300 text-sm">
                        {item.division || "—"}
                      </div>
                    </td>
                    
                    {/* Columna POSICIÓN */}
                    <td className="py-3 px-3 text-center">
                      {item.posicion !== null && item.posicion !== undefined ? (
                        <span className="text-lg font-bold" style={{ color: "#A51B3D" }}>
                          {item.posicion}º
                        </span>
                      ) : (
                        <span className="text-slate-500 text-sm">—</span>
                      )}
                    </td>
                    
                    {/* Columna PUNTOS */}
                    <td className="py-3 px-3 text-center">
                      {item.puntos !== null && item.puntos !== undefined ? (
                        <span className="text-white font-bold text-sm">
                          {item.puntos}
                        </span>
                      ) : (
                        <span className="text-slate-500 text-sm">—</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="py-4 px-3 text-center text-slate-400 text-sm">
                    {H.no_data || "No hay temporadas históricas disponibles"}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function ClubDetailClient({ lang, clubId, dict }: Props) {
  const [data, setData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!clubId) {
      setLoading(false);
      setError(dict?.club_detail?.invalid_id || "ID de club no válido");
      return;
    }
    const controller = new AbortController();

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
        
        // Determinar si es ID numérico o slug
        const isNumeric = /^\d+$/.test(String(clubId).trim());
        const paramName = isNumeric ? "club_id" : "slug";
        
        const url = `${base}/api/clubes/full/?${paramName}=${encodeURIComponent(clubId)}`;
        
        const res = await fetch(url, {
          signal: controller.signal,
          cache: "no-store",
        });
        
        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`Error ${res.status}: ${errorText || dict?.club_detail?.error_loading || "Error cargando la ficha del club"}`);
        }
        
        const json = await res.json();
        
        if (!json || !json.club) {
          throw new Error(dict?.club_detail?.invalid_response || "Respuesta del servidor inválida: no se encontró el club");
        }
        
        setData(json);
      } catch (err: any) {
        if (err.name !== "AbortError") {
          console.error("Error loading club:", err);
          setError(err.message || dict?.club_detail?.error || "Error al cargar el club");
        }
      } finally {
        setLoading(false);
      }
    };

    load();
    return () => controller.abort();
  }, [clubId]);

  const L = dict?.club_detail || {};

  if (loading) {
    return (
      <div className="px-4 md:px-8 py-6 text-slate-200 text-sm">
        {L.loading || "Cargando club..."}
      </div>
    );
  }

  if (error || !data?.club) {
    return (
      <div className="px-4 md:px-8 py-6 text-red-400 text-sm">
        {error || L.not_found || "Club no encontrado."}
      </div>
    );
  }

  const club = data.club || {};
  const ctx = data.contexto; // { temporada, grupo } o null
  const clasif = club.clasificacion_actual || {};

  const clubName = club?.nombre_corto || club?.nombre_oficial || (L.club_fallback || "Club");
  const escudo = club?.escudo_url || "";
  const grupoNombre = ctx?.grupo?.nombre || "";
  const competicionNombre = ctx?.grupo?.competicion || "";
  const grupoSlug = ctx?.grupo?.slug || "";
  const competicionSlug = ctx?.grupo?.competicion_slug || "";
  
  // Colores del club
  const colorPrimario = club?.colores?.primario || "";
  const colorSecundario = club?.colores?.secundario || "";
  const tieneColores = (colorPrimario && colorPrimario.trim()) || (colorSecundario && colorSecundario.trim());

  // Construir URL de clasificación
  const clasificacionUrl = grupoSlug && competicionSlug
    ? `/${lang}/clasificacion/${competicionSlug}/${grupoSlug}`
    : null;

  return (
    <div className="px-4 md:px-8 py-6 space-y-6">
      {/* Header con escudo, nombre y división */}
      <div 
        className="relative overflow-hidden rounded-2xl border border-white/10 p-6 md:p-8"
        style={{
          background: colorPrimario 
            ? `linear-gradient(135deg, ${colorPrimario}15 0%, rgba(0,0,0,0.3) 100%)`
            : "linear-gradient(135deg, rgba(165,27,61,0.15) 0%, rgba(0,0,0,0.3) 100%)"
        }}
      >
        {/* Patrón de fondo decorativo */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `repeating-linear-gradient(45deg, transparent, transparent 10px, currentColor 10px, currentColor 20px)`
          }}></div>
        </div>
        
        <div className="relative flex flex-col md:flex-row md:items-center gap-6">
          {/* Escudo */}
          {escudo && (
            <div className="flex-shrink-0">
              <div 
                className="w-24 h-24 md:w-32 md:h-32 rounded-xl p-3 border-2 border-white/10 shadow-lg"
                style={{
                  background: colorPrimario 
                    ? `linear-gradient(135deg, ${colorPrimario}30, rgba(255,255,255,0.1))`
                    : "linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))"
                }}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={escudo}
                  alt={clubName}
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}
          
          {/* Información principal */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h1 className="text-3xl md:text-4xl font-bold text-white">
                {clubName}
              </h1>
              {club?.siglas && (
                <span className="px-2 py-1 rounded text-xs font-semibold bg-white/10 text-slate-300 border border-white/10">
                  {club.siglas}
                </span>
              )}
            </div>
            {club?.nombre_oficial && club.nombre_oficial !== clubName && (
              <p className="text-slate-300 text-sm mb-3">
                {club.nombre_oficial}
              </p>
            )}
            
            {/* División y grupo */}
            {(competicionNombre || grupoNombre) && (
              <div className="flex flex-wrap items-center gap-2">
                <span 
                  className="px-3 py-1 rounded-full text-xs font-semibold text-white border border-white/10"
                  style={{
                    background: colorPrimario ? `${colorPrimario}40` : "rgba(165,27,61,0.3)"
                  }}
                >
                  {competicionNombre}
                  {competicionNombre && grupoNombre && " · "}
                  {grupoNombre}
                </span>
              </div>
            )}
          </div>

          {/* Colores del club */}
          {tieneColores && (
            <div className="flex flex-col gap-2">
              <Label>{L.colors_title || "Colores del club"}</Label>
              <div className="flex items-center gap-2">
                {colorPrimario && (
                  <div
                    className="w-8 h-8 rounded-lg border-2 border-white/10 shadow-md"
                    style={{ backgroundColor: colorPrimario }}
                    title={`${L.primary_color || "Color primario"}: ${colorPrimario}`}
                  />
                )}
                {colorSecundario && (
                  <div
                    className="w-8 h-8 rounded-lg border-2 border-white/10 shadow-md"
                    style={{ backgroundColor: colorSecundario }}
                    title={`${L.secondary_color || "Color secundario"}: ${colorSecundario}`}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Reconocimientos MVP y Fantasy */}
      {club.id && (
        <EquipoReconocimientosCard
          clubId={club.id}
          dict={dict}
          lang={lang}
        />
      )}

      {/* Grid de información básica - 2 columnas */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Primera columna: Información del club + Contacto apilados */}
        <div className="space-y-4">
          {/* Información del club */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-4">
            <h2 className="text-lg font-semibold text-white border-b border-white/10 pb-2">
              {L.info_title || "Información del club"}
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {club?.pabellon && (
                <Stat label={L.labels?.pabellon || "Pabellón"} value={club.pabellon} />
              )}
              {club?.fundado_en && (
                <Stat label={L.labels?.fundado || "Fundado"} value={club.fundado_en} />
              )}
              {club?.aforo_aprox && (
                <Stat label={L.labels?.aforo || "Aforo"} value={`${club.aforo_aprox.toLocaleString()} ${L.aforo_suffix || "personas"}`} />
              )}
              {club?.ciudad && (
                <Stat label={L.labels?.ciudad || "Ciudad"} value={club.ciudad} />
              )}
              {club?.provincia && (
                <Stat label={L.labels?.provincia || "Provincia"} value={club.provincia} />
              )}
            </div>
            {club?.direccion && (
              <div className="pt-2 border-t border-white/10">
                <Label>{L.labels?.direccion || "Dirección"}</Label>
                <p className="text-white text-sm mt-1">{club.direccion}</p>
              </div>
            )}
          </div>

          {/* Contacto - Justo debajo de Información del club */}
          {(club?.web || club?.contacto?.email || club?.contacto?.telefono) && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-4">
              <h2 className="text-lg font-semibold text-white border-b border-white/10 pb-2">
                {L.contact_title || "Contacto"}
              </h2>
              <div className="space-y-3">
                {club?.web && (
                  <div>
                    <Label>{L.labels?.web || "Web oficial"}</Label>
                    <a
                      href={club.web}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-300 hover:text-blue-200 hover:underline break-all text-sm mt-1 block"
                    >
                      {club.web}
                    </a>
                  </div>
                )}
                {club?.contacto?.email && (
                  <div>
                    <Label>{L.labels?.email || "Email"}</Label>
                    <a
                      href={`mailto:${club.contacto.email}`}
                      className="text-blue-300 hover:text-blue-200 hover:underline break-all text-sm mt-1 block"
                    >
                      {club.contacto.email}
                    </a>
                  </div>
                )}
                {club?.contacto?.telefono && (
                  <div>
                    <Label>{L.labels?.telefono || "Teléfono"}</Label>
                    <a
                      href={`tel:${club.contacto.telefono}`}
                      className="text-blue-300 hover:text-blue-200 hover:underline text-sm mt-1 block"
                    >
                      {club.contacto.telefono}
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Segunda columna: Clasificación + Redes sociales apilados */}
        <div className="space-y-4">
          {/* Clasificación actual */}
          {clasif && Object.keys(clasif).length > 0 && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-4">
              <h2 className="text-lg font-semibold text-white border-b border-white/10 pb-2">
                {L.classification_title || "Clasificación"} {ctx?.temporada?.nombre ? `(${ctx.temporada.nombre})` : ""}
              </h2>
              
              {/* Posición y puntos */}
              <div className="grid grid-cols-2 gap-4">
                {clasif.posicion !== null && clasif.posicion !== undefined && (
                  <Stat 
                    label={L.labels?.posicion || "Posición"} 
                    value={
                      <span className="text-2xl font-bold" style={{ color: colorPrimario || "#A51B3D" }}>
                        {clasif.posicion}º
                      </span>
                    } 
                  />
                )}
                {clasif.puntos !== null && clasif.puntos !== undefined && (
                  <Stat label={L.labels?.puntos || "Puntos"} value={clasif.puntos} />
                )}
              </div>

              {/* Partidos ganados, empatados, perdidos */}
              <div className="grid grid-cols-3 gap-3 pt-2 border-t border-white/10">
                <Stat 
                  label={L.labels?.ganados || "Ganados"} 
                  value={<span className="text-green-400">{clasif.v ?? 0}</span>} 
                />
                <Stat 
                  label={L.labels?.empatados || "Empatados"} 
                  value={<span className="text-yellow-400">{clasif.e ?? 0}</span>} 
                />
                <Stat 
                  label={L.labels?.perdidos || "Perdidos"} 
                  value={<span className="text-red-400">{clasif.d ?? 0}</span>} 
                />
              </div>

              {/* Goles a favor y en contra */}
              <div className="grid grid-cols-2 gap-4 pt-2 border-t border-white/10">
                <Stat 
                  label={L.labels?.goles_favor || "Goles a favor"} 
                  value={clasif.gf ?? 0} 
                />
                <Stat 
                  label={L.labels?.goles_contra || "Goles en contra"} 
                  value={clasif.gc ?? 0} 
                />
              </div>
              
              {/* Tarjetas */}
              <div className="pt-2 border-t border-white/10">
                <Label>{L.labels?.tarjetas_temporada || "Tarjetas esta temporada"}</Label>
                <div className="grid grid-cols-3 gap-3 mt-2">
                  <div className="flex flex-col items-center p-2 rounded bg-white/5">
                    <span className="text-yellow-400 text-lg font-bold">
                      {clasif.tarjetas_amarillas ?? 0}
                    </span>
                    <span className="text-xs text-slate-300 mt-1">{L.labels?.amarillas || "Amarillas"}</span>
                  </div>
                  <div className="flex flex-col items-center p-2 rounded bg-white/5">
                    <span className="text-orange-400 text-lg font-bold">
                      {clasif.tarjetas_dobles_amarillas ?? 0}
                    </span>
                    <span className="text-xs text-slate-300 mt-1">{L.labels?.dobles_amarillas || "Dobles Amarillas"}</span>
                  </div>
                  <div className="flex flex-col items-center p-2 rounded bg-white/5">
                    <span className="text-red-400 text-lg font-bold">
                      {clasif.tarjetas_rojas ?? 0}
                    </span>
                    <span className="text-xs text-slate-300 mt-1">{L.labels?.rojas || "Rojas"}</span>
                  </div>
                </div>
              </div>

              {/* Botón ver clasificación */}
              {clasificacionUrl && (
                <div className="pt-2 border-t border-white/10">
                  <Link
                    href={clasificacionUrl}
                    className="block w-full text-center px-4 py-2 rounded-lg font-semibold text-sm transition-colors"
                    style={{
                      background: colorPrimario || "rgba(165,27,61,0.8)",
                      color: "white",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.opacity = "0.9";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.opacity = "1";
                    }}
                  >
                    {L.labels?.ver_clasificacion || "Ver clasificación completa"}
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Histórico de temporadas - SIEMPRE VISIBLE */}
          <HistoricoTemporadas clubId={clubId} tempActual={ctx?.temporada?.nombre} dict={dict} />

          {/* Redes sociales - Debajo de Clasificación */}
          {(club?.redes?.twitter ||
            club?.redes?.instagram ||
            club?.redes?.facebook ||
            club?.redes?.tiktok ||
            club?.redes?.youtube) && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-4">
              <h2 className="text-lg font-semibold text-white border-b border-white/10 pb-2">
                {L.social_media_title || "Redes sociales"}
              </h2>
              <div className="flex flex-wrap gap-2">
                {club?.redes?.twitter && (
                  <a
                    href={club.redes.twitter}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 text-white text-sm font-medium transition-colors"
                  >
                    Twitter
                  </a>
                )}
                {club?.redes?.instagram && (
                  <a
                    href={club.redes.instagram}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 text-white text-sm font-medium transition-colors"
                  >
                    Instagram
                  </a>
                )}
                {club?.redes?.facebook && (
                  <a
                    href={club.redes.facebook}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 text-white text-sm font-medium transition-colors"
                  >
                    Facebook
                  </a>
                )}
                {club?.redes?.tiktok && (
                  <a
                    href={club.redes.tiktok}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 text-white text-sm font-medium transition-colors"
                  >
                    TikTok
                  </a>
                )}
                {club?.redes?.youtube && (
                  <a
                    href={club.redes.youtube}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 text-white text-sm font-medium transition-colors"
                  >
                    YouTube
                  </a>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Plantilla (Jugadores) */}
      {club.plantilla && Array.isArray(club.plantilla) && club.plantilla.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-4">
          <h2 className="text-lg font-semibold text-white border-b border-white/10 pb-2">
            {L.plantilla_title || "Plantilla"} {ctx?.temporada?.nombre ? `(${ctx.temporada.nombre})` : ""}
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {club.plantilla.map((jugador: any) => (
              <JugadorCard key={jugador.id} jugador={jugador} lang={lang} dict={dict} />
            ))}
          </div>
        </div>
      )}

      {/* Staff */}
      {club.staff && Array.isArray(club.staff) && club.staff.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-4">
          <h2 className="text-lg font-semibold text-white border-b border-white/10 pb-2">
            {L.staff_title || "Cuerpo técnico"} {ctx?.temporada?.nombre ? `(${ctx.temporada.nombre})` : ""}
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {club.staff.map((miembro: any, idx: number) => (
              <StaffCard key={idx} miembro={miembro} dict={dict} />
            ))}
          </div>
        </div>
      )}

      {/* CONTENIDO EDITORIAL - CLUB */}
      {dict?.editorial?.club && (
        <div className="bg-brand-card border border-brand-card rounded-lg p-6 space-y-4">
          <h2 className="text-xl font-bold text-brand-text">
            {dict.editorial.club.title || "Perfil del Club"}
          </h2>
          <div className="space-y-3 text-sm text-brand-textSecondary leading-relaxed">
            <p>{dict.editorial.club.paragraph1}</p>
            <p>{dict.editorial.club.paragraph2}</p>
            <p>{dict.editorial.club.paragraph3}</p>
          </div>
        </div>
      )}
    </div>
  );
}

// Componente para mostrar una tarjeta de jugador
function JugadorCard({
  jugador,
  dict,
  lang,
}: {
  jugador: {
    id: number;
    nombre: string;
    apodo?: string;
    slug?: string | null;
    foto_url?: string;
    posicion_principal?: string;
    dorsal?: string | null;
    partidos_jugados?: number;
    goles?: number;
    edad_display?: number | null;
  };
  dict: any;
  lang: string;
}) {
  const nombre = jugador.apodo || jugador.nombre;
  const href = `/${lang}/jugadores/${jugador.slug || jugador.id}`;

  return (
    <Link
      href={href}
      className="block py-3 px-3 bg-white/5 rounded-xl border border-white/10 hover:border-white/30 hover:bg-white/10 transition"
      aria-label={`${dict?.jugadores_page?.see_more || "ver jugador"}: ${nombre}`}
    >
      <div className="flex flex-col items-center gap-3">
        <div className="w-14 h-14 rounded-full bg-[#111] border border-white/10 flex items-center justify-center overflow-hidden">
          {jugador.foto_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={jugador.foto_url}
              alt={nombre}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <span className="text-[0.6rem] text-white/40">
              {nombre?.slice(0, 2)?.toUpperCase()}
            </span>
          )}
        </div>

        <div className="flex flex-col items-center text-center">
          <span className="text-sm font-medium text-white">{nombre}</span>
          {jugador.posicion_principal ? (
            <span className="text-xs text-white/50">{jugador.posicion_principal}</span>
          ) : null}
          {jugador.dorsal ? (
            <span className="text-xs text-white/60">#{jugador.dorsal}</span>
          ) : null}
        </div>

        {/* Mini-stats */}
        {(jugador.goles != null || jugador.partidos_jugados != null || jugador.edad_display != null) && (
          <div className="flex flex-wrap items-center justify-center gap-2 text-[11px] text-white/80">
            {jugador.edad_display != null && (
              <Chip label={dict?.jugadores_page?.age || "EDAD"} value={jugador.edad_display} />
            )}
            {jugador.goles != null && jugador.goles > 0 && (
              <Chip label={dict?.jugadores_page?.goals || "GOLES"} value={jugador.goles} />
            )}
            {jugador.partidos_jugados != null && jugador.partidos_jugados > 0 && (
              <Chip label={dict?.jugadores_page?.matches || "PJ"} value={jugador.partidos_jugados} />
            )}
          </div>
        )}

        {/* CTA */}
        <div className="text-[0.65rem] uppercase tracking-wide text-brand-accent hover:underline">
          {dict?.jugadores_page?.see_more || "ver jugador"}
        </div>
      </div>
    </Link>
  );
}

// Componente para mostrar una tarjeta de staff
function StaffCard({
  miembro,
  dict,
}: {
  miembro: {
    nombre: string;
    rol: string;
    email?: string;
    telefono?: string;
  };
  dict: any;
}) {
  return (
    <div className="py-3 px-3 bg-white/5 rounded-xl border border-white/10">
      <div className="flex flex-col items-center gap-3">
        <div className="w-14 h-14 rounded-full bg-[#111] border border-white/10 flex items-center justify-center">
          <span className="text-[0.6rem] text-white/40">
            {miembro.nombre?.slice(0, 2)?.toUpperCase()}
          </span>
        </div>

        <div className="flex flex-col items-center text-center">
          <span className="text-sm font-medium text-white">{miembro.nombre}</span>
          {miembro.rol ? (
            <span className="text-xs text-white/60">{miembro.rol}</span>
          ) : null}
        </div>

        {(miembro.email || miembro.telefono) && (
          <div className="flex flex-col items-center gap-1 text-[10px] text-white/60">
            {miembro.email && (
              <a
                href={`mailto:${miembro.email}`}
                className="hover:text-white/80 hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                {miembro.email}
              </a>
            )}
            {miembro.telefono && (
              <a
                href={`tel:${miembro.telefono}`}
                className="hover:text-white/80 hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                {miembro.telefono}
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Componente Chip reutilizable
function Chip({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-white/5 border border-white/10 px-2 py-0.5">
      <span className="text-white/50">{label}</span>
      <span className="text-white">{value}</span>
    </span>
  );
}
