"use client";

import React from "react";

type EmptyStateProps = {
  dict?: any;
  type?: "home" | "competicion" | "clubes" | "rankings" | "clasificacion" | "mvp" | "general";
  variant?: "no_matches" | "no_classification" | "no_players" | "no_teams" | "no_clubs" | "no_matches" | "no_goals" | "no_mvp" | "no_history" | "no_sanctions" | "loading" | "error" | "no_data_generic";
  customMessage?: string;
  className?: string;
};

export default function EmptyState({ 
  dict, 
  type = "general", 
  variant = "no_data_generic",
  customMessage,
  className = ""
}: EmptyStateProps) {
  // Obtener el mensaje del diccionario
  const getMessage = () => {
    if (customMessage) return customMessage;
    
    const emptyStates = dict?.empty_states;
    if (!emptyStates) {
      // Fallback hardcoded si no hay diccionario
      return "No hay datos disponibles en este momento.";
    }

    // Intentar obtener el mensaje específico
    if (type !== "general" && emptyStates[type] && emptyStates[type][variant]) {
      return emptyStates[type][variant];
    }

    // Fallback al general
    if (emptyStates.general && emptyStates.general[variant]) {
      return emptyStates.general[variant];
    }

    // Último fallback
    return emptyStates.general?.no_data_generic || "No hay datos disponibles en este momento.";
  };

  const message = getMessage();
  const isError = variant === "error";
  const isLoading = variant === "loading";

  return (
    <div 
      className={`text-xs ${
        isError 
          ? "text-[var(--color-error)]" 
          : isLoading
          ? "text-[var(--color-text-secondary)]"
          : "text-[var(--color-text-secondary)]"
      } ${className}`}
    >
      {message}
    </div>
  );
}















