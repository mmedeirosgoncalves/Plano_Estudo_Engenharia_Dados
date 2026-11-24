import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from plan_lib import day_from_title, issue_body, issue_title, load_plan, study_days  # noqa: E402

PLAN = load_plan()


def test_trinta_dias_em_sequencia():
    assert [d["day"] for d in PLAN["days"]] == list(range(1, 31))


def test_fases_cobrem_os_dias():
    for day in PLAN["days"]:
        phase = next(p for p in PLAN["phases"] if p["id"] == day["phase"])
        start, end = phase["days"]
        assert start <= day["day"] <= end, day["day"]


def test_dias_de_estudo_tem_conteudo():
    for day in study_days(PLAN):
        assert day["study"], day["day"]
        assert day["evidence"], day["day"]


def test_links_sao_https():
    for day in PLAN["days"]:
        for link in day["links"]:
            assert link["url"].startswith("https://"), link


def test_titulo_da_issue_ida_e_volta():
    for day in study_days(PLAN):
        assert day_from_title(issue_title(day)) == day["day"]


def test_corpo_da_issue_lista_os_temas():
    day = study_days(PLAN)[0]
    body = issue_body(day)
    for item in day["study"]:
        assert f"- [ ] {item}" in body
