// /components/PartidoStaff.tsx
"use client";

import React from "react";

type PartidoStaffProps = {
  staff: {
    local: {
      staff: Array<{
        nombre: string;
        rol: string;
        staff_id: number | null;
      }>;
    };
    visitante: {
      staff: Array<{
        nombre: string;
        rol: string;
        staff_id: number | null;
      }>;
    };
  };
  dict: any;
  lang: string;
};

export default function PartidoStaff({
  staff,
  dict,
  lang,
}: PartidoStaffProps) {
  if (
    staff.local.staff.length === 0 &&
    staff.visitante.staff.length === 0
  ) {
    return null;
  }

  return (
    <div className="bg-brand-card rounded-xl border border-[var(--color-navy)] shadow-xl p-6">
      <h2 className="text-2xl font-bold text-white mb-6 font-[var(--font-title)]">
        {dict?.partidos?.staff_title || "Staff Técnico"}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Staff Local */}
        {staff.local.staff.length > 0 && (
          <div>
            <div className="bg-[var(--color-navy)] rounded-lg p-4 mb-4 border border-[var(--color-accent)]/30">
              <h3 className="text-lg font-bold text-white">
                {dict?.partidos?.local || "Local"}
              </h3>
            </div>
            <div className="space-y-2">
              {staff.local.staff.map((s, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 bg-[var(--color-navy)] rounded-lg border border-[var(--color-navy)]/50 hover:border-[var(--color-accent)]/50 transition-all"
                >
                  <div className="flex-1">
                    <div className="text-sm font-bold text-white">
                      {s.nombre}
                    </div>
                    {s.rol && (
                      <div className="text-xs text-white/60 mt-1">
                        {s.rol}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Staff Visitante */}
        {staff.visitante.staff.length > 0 && (
          <div>
            <div className="bg-[var(--color-navy)] rounded-lg p-4 mb-4 border border-[var(--color-accent)]/30">
              <h3 className="text-lg font-bold text-white">
                {dict?.partidos?.visitante || "Visitante"}
              </h3>
            </div>
            <div className="space-y-2">
              {staff.visitante.staff.map((s, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 bg-[var(--color-navy)] rounded-lg border border-[var(--color-navy)]/50 hover:border-[var(--color-accent)]/50 transition-all"
                >
                  <div className="flex-1">
                    <div className="text-sm font-bold text-white">
                      {s.nombre}
                    </div>
                    {s.rol && (
                      <div className="text-xs text-white/60 mt-1">
                        {s.rol}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
