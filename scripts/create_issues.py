"""Cria label, milestones (uma por fase) e uma issue por dia de estudo.

Idempotente: o que já existe não é recriado. Rode pelo workflow
"Criar issues do plano" (Actions > Run workflow).
"""
from __future__ import annotations

from github_api import GitHub
from plan_lib import (day_from_title, issue_body, issue_title, load_plan,
                      milestone_title, phase_of, study_days)


def main() -> None:
    gh = GitHub()
    plan = load_plan()
    repo = f"/repos/{gh.repo}"
    label = plan["issue_label"]

    labels = {l["name"] for l in gh.paginate(f"{repo}/labels")}
    if label not in labels:
        gh.post(f"{repo}/labels", {"name": label, "color": "e4572e",
                                   "description": "Dia do plano de estudos"})
        print(f"label criada: {label}")
    if "estudando" not in labels:
        gh.post(f"{repo}/labels", {"name": "estudando", "color": "f4b942",
                                   "description": "Dia em andamento"})

    milestones = {m["title"]: m["number"]
                  for m in gh.paginate(f"{repo}/milestones", {"state": "all"})}
    for phase in plan["phases"]:
        title = milestone_title(phase)
        if title not in milestones:
            m = gh.post(f"{repo}/milestones", {"title": title, "description": phase["result"]})
            milestones[title] = m["number"]
            print(f"milestone criada: {title}")

    existing = {day_from_title(i["title"])
                for i in gh.paginate(f"{repo}/issues", {"state": "all", "labels": label})
                if "pull_request" not in i}

    for day in study_days(plan):
        if day["day"] in existing:
            continue
        gh.post(f"{repo}/issues", {
            "title": issue_title(day),
            "body": issue_body(day),
            "labels": [label],
            "milestone": milestones[milestone_title(phase_of(plan, day))],
        })
        print(f"issue criada: {issue_title(day)}")


if __name__ == "__main__":
    main()
