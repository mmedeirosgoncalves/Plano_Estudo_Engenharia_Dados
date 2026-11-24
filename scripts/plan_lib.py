"""Leitura do plano e convenções compartilhadas entre os scripts."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = ROOT / "plan" / "plan.json"
TITLE_RE = re.compile(r"^Dia (\d{2})\b")


def load_plan(path: Path = PLAN_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def study_days(plan: dict) -> list[dict]:
    return [d for d in plan["days"] if not d.get("rest")]


def phase_of(plan: dict, day: dict) -> dict:
    return next(p for p in plan["phases"] if p["id"] == day["phase"])


def milestone_title(phase: dict) -> str:
    return f"Fase {phase['id']} – {phase['name']}"


def issue_title(day: dict) -> str:
    return f"Dia {day['day']:02d} · {day['title']}"


def day_from_title(title: str) -> int | None:
    m = TITLE_RE.match(title)
    return int(m.group(1)) if m else None


def issue_body(day: dict) -> str:
    lines = ["### Estudo", ""]
    lines += [f"- [ ] {item}" for item in day["study"]]
    if day.get("evidence"):
        lines += ["", "### Evidência do dia", "", day["evidence"]]
    if day.get("project"):
        lines += ["", "### Projeto final", "", f"- [ ] {day['project']}"]
    if day.get("links"):
        lines += ["", "### Materiais", ""]
        lines += [f"- [{l['title']}]({l['url']})" for l in day["links"]]
    lines += ["", "---", "Feche esta issue quando terminar o dia. O painel atualiza sozinho."]
    return "\n".join(lines)
