# scraping/management/commands/scrape_todo.py
import time, random
from django.core.management import call_command
from django.core.management.base import BaseCommand
from scraping.core.config_temporadas import TEMPORADAS

class Command(BaseCommand):
    help = "Scrapea temporadas en orden descendente. 2025-2026 solo J1–J5 en TODOS los grupos; el resto completas."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("🏁 Iniciando scraping múltiple (orden descendente, sólo J1–J5)"))

        temporadas_en_orden = ["2025-2026", "2024-2025", "2023-2024", "2022-2023"]

        for temporada_key in temporadas_en_orden:
            cfg = TEMPORADAS.get(temporada_key)
            if not cfg:
                self.stderr.write(self.style.ERROR(f"⛔ La temporada {temporada_key} no está en config_temporadas.py"))
                continue

            # Determinar nº jornadas base
            jornadas_base = cfg.get("jornadas", 30)
            # Regla: 2025-2026 solo hasta 5
            total_jornadas = 5 if temporada_key == "2025-2026" else jornadas_base

            # === 2.1) TERCERA ===
            grupos_tercera = []
            if "grupos" in cfg:
                # Fuerza orden XV -> XIV si existen
                if "XV" in cfg["grupos"]:
                    grupos_tercera.append(("XV", cfg["grupos"]["XV"]))
                if "XIV" in cfg["grupos"]:
                    grupos_tercera.append(("XIV", cfg["grupos"]["XIV"]))
                # Si hay más grupos, añádelos después en orden alfabético
                for k in sorted(cfg["grupos"].keys()):
                    if k not in ("XV", "XIV"):
                        grupos_tercera.append((k, cfg["grupos"][k]))

            total_grupos = len(grupos_tercera)
            self.stdout.write(self.style.NOTICE(
                f"\n📅 Temporada {temporada_key}: {total_grupos} grupo(s) TERCERA · se procesarán J1–J{total_jornadas}\n"
            ))

            for idx, (gkey, gmeta) in enumerate(grupos_tercera, start=1):
                self.stdout.write(self.style.MIGRATE_HEADING(
                    f"🏷️  {temporada_key} · TERCERA · {gkey}  ({idx}/{total_grupos})"
                ))
                for j in range(1, total_jornadas + 1):
                    self.stdout.write(self.style.HTTP_INFO(
                        f"→ Jornada {j}/{total_jornadas} · TERCERA {gkey}"
                    ))
                    try:
                        call_command("scrape_jornada",
                                     temporada=temporada_key,
                                     jornada=j,
                                     competicion="TERCERA",
                                     grupo=gkey)
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(
                            f"⚠️  Error en {temporada_key} TERCERA {gkey} J{j}: {e}"
                        ))
                        continue

                    # pausa cada 5–6 jornadas
                    if j % random.choice([5, 6]) == 0 and j != total_jornadas:
                        pausa = random.randint(6, 12)
                        self.stdout.write(self.style.WARNING(
                            f"⏳ Pausa entre jornadas ({pausa}s)…"
                        ))
                        time.sleep(pausa)

                # pequeña pausa entre grupos
                time.sleep(random.uniform(3.0, 6.0))

            # === 2.2) OTRAS COMPETICIONES (Preferente / Primera / Segunda) ===
            otras = cfg.get("otras_competiciones", {})
            for comp_name, comp_node in otras.items():
                grupos = comp_node.get("grupos", {})
                # Ordena G1, G2, G3… numéricamente si es posible
                def sort_key(k):
                    try:
                        return int(k.lstrip("Gg"))
                    except Exception:
                        return k
                grupos_ordenados = sorted(grupos.keys(), key=sort_key)

                for gk in grupos_ordenados:
                    gmeta = grupos[gk]
                    # jornadas específicas del grupo o las de la temporada;
                    # y respeta el límite de 5 en 2025-2026
                    j_total = gmeta.get("jornadas", jornadas_base)
                    if temporada_key == "2025-2026":
                        j_total = min(j_total, 5)

                    self.stdout.write(self.style.MIGRATE_HEADING(
                        f"🏷️  {temporada_key} · {comp_name.upper()} · {gk}"
                    ))
                    for j in range(1, j_total + 1):
                        self.stdout.write(self.style.HTTP_INFO(
                            f"→ Jornada {j}/{j_total} · {comp_name.upper()} {gk}"
                        ))
                        try:
                            # Mapea nombre CLI de competición a tus claves admitidas por scrape_jornada
                            cli_comp = ("PREFERENTE" if "Preferente" in comp_name
                                        else "PRIMERA" if "Primera Regional" in comp_name
                                        else "SEGUNDA")
                            call_command("scrape_jornada",
                                         temporada=temporada_key,
                                         jornada=j,
                                         competicion=cli_comp,
                                         grupo=gk)
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(
                                f"⚠️  Error en {temporada_key} {comp_name} {gk} J{j}: {e}"
                            ))
                            continue

                        if j % random.choice([5, 6]) == 0 and j != j_total:
                            pausa = random.randint(6, 12)
                            self.stdout.write(self.style.WARNING(
                                f"⏳ Pausa entre jornadas ({pausa}s)…"
                            ))
                            time.sleep(pausa)

                    time.sleep(random.uniform(3.0, 6.0))

            # Pausa larga entre temporadas
            if temporada_key != temporadas_en_orden[-1]:
                pausa_temporada = random.randint(12, 25)
                self.stdout.write(self.style.WARNING(
                    f"\n🌙 Pausa entre temporadas ({pausa_temporada}s)…\n"
                ))
                time.sleep(pausa_temporada)

        self.stdout.write(self.style.SUCCESS("\n✅ Scraping completado en todas las temporadas/grupos."))
