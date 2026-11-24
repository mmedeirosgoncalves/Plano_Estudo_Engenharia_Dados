# Plano de estudos – Engenharia de Dados em 30 dias

Painel pessoal para acompanhar um plano de 30 dias de engenharia de dados: fundamentos, SQL e modelagem, Python, Spark, nuvem (Azure e AWS), Lakehouse, streaming, DataOps, segurança, governança, observabilidade e FinOps, fechando com um projeto de ponta a ponta.

**Painel:** https://mmedeirosgoncalves.github.io/Plano_Estudo_Engenharia_Dados/

## Como funciona

```
plan/plan.json ──► issues (uma por dia, milestones por fase)
       │                    │ fechar issue = dia concluído
       ▼                    ▼
  GitHub Actions ──► _site/ + progress.json ──► GitHub Pages
```

- Cada dia de estudo é uma issue com checklist, evidência esperada e materiais.
- **Fechar a issue** marca o dia como concluído. A label `estudando` marca o dia em andamento.
- A cada mudança nas issues (e uma vez por dia), o workflow **Publicar painel** roda os testes, lê as issues e republica o site.
- No celular, use o app do GitHub para fechar issues; o painel abre em qualquer navegador.

## Configuração (uma vez)

1. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
2. **Actions → Criar issues do plano → Run workflow.** Cria a label, as 5 milestones e as 26 issues, e já republica o painel. Pode rodar de novo sem duplicar nada.
3. (Opcional) Defina `start_date` em `plan/plan.json` (formato `AAAA-MM-DD`) para o calendário mostrar datas e o seu ritmo. Também dá para escolher a data direto no painel, mas aí ela fica só naquele navegador.
4. (Opcional) Crie um quadro em **Projects** com as issues da label `plano-estudo` para ter um Kanban.

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `plan/plan.json` | O plano: fases, dias, temas, evidências e links |
| `site/` | Painel estático (HTML, CSS, JS, sem dependências) |
| `scripts/create_issues.py` | Cria label, milestones e issues a partir do plano |
| `scripts/build_site.py` | Monta o site e gera `progress.json` a partir das issues |
| `tests/` | Testes do plano (rodam no CI antes de publicar) |
| `.github/workflows/` | Publicação do painel e criação das issues |

## Rodar localmente

```bash
python -m venv .venv && source .venv/bin/activate
pip install pytest
pytest -q
python scripts/build_site.py --out _site --offline
python -m http.server -d _site 8000   # abra http://localhost:8000
```

## Editar o plano

Altere `plan/plan.json` e faça push. Os testes validam a estrutura; o painel é republicado. Para dias novos, rode de novo **Criar issues do plano**. Issues que já existem não são alteradas, então ajuste o texto delas à mão se mudar um dia existente.

Todo o conteúdo usa só documentação pública.
