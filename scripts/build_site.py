"""Monta a pasta do site: copia o plano e gera progress.json a partir das issues.

Uso:
  python scripts/build_site.py --out _site            # lê as issues pela API
  python scripts/build_site.py --out _site --offline  # sem API (teste local)
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from plan_lib import ROOT, day_from_title, load_plan


def fetch_progress(label: str) -> dict:
    from github_api import GitHub

    gh = GitHub()
    issues = gh.paginate(f"/repos/{gh.repo}/issues", {"state": "all", "labels": label})
    days: dict[str, dict] = {}
    for issue in issues:
        if "pull_request" in issue:
            continue
        n = day_from_title(issue["title"])
        if n is None:
            continue
        labels = {l["name"] for l in issue.get("labels", [])}
        state = "done" if issue["state"] == "closed" else (
            "doing" if "estudando" in labels else "todo")
        days[str(n)] = {"state": state, "url": issue["html_url"],
                        "number": issue["number"], "closed_at": issue.get("closed_at")}
    return {"repo": gh.repo, "days": days}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="_site")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT / "site", out)
    (out / "data").mkdir(exist_ok=True)

    plan = load_plan()
    shutil.copy(ROOT / "plan" / "plan.json", out / "data" / "plan.json")

    progress = {"repo": None, "days": {}} if args.offline else fetch_progress(plan["issue_label"])
    progress["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (out / "data" / "progress.json").write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")
    done = sum(1 for d in progress["days"].values() if d["state"] == "done")
    print(f"site gerado em {out} – {done} dias concluídos")


if __name__ == "__main__":
    main()
