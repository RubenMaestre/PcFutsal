"use client";

import React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { usePathname } from "next/navigation";

// Componente wrapper que añade animaciones de transición entre páginas.
// Usa framer-motion para crear transiciones suaves cuando cambia la ruta.
// El key={pathname} asegura que cada página tenga su propia animación.
export default function AnimatedShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        // Animación de entrada: fade in + slide up
        initial={{ opacity: 0, y: 15 }}
        // Estado final: completamente visible y en posición
        animate={{ opacity: 1, y: 0 }}
        // Animación de salida: fade out + slide down
        exit={{ opacity: 0, y: -15 }}
        // Duración y easing para transición suave
        transition={{ duration: 0.25, ease: "easeInOut" }}
        className="w-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
