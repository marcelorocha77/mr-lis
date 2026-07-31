# Projeto LIS — Sistema MR

Sistema de gestão de laboratório clínico moderno, sucessor conceitual do TM Informatica. SaaS multi-tenant, arquitetura modular.

## Módulos

| Módulo | Responsabilidade | Rota base |
|---|---|---|
| **MRLAB** | Núcleo — pacientes, médicos, convênios, requisições, coleta, agenda | `/mrlab/*` |
| **MRLABLaudo** | Emissão e liberação de laudos | `/mrlablaudo/*` |
| **MRQuality** | Controle de qualidade analítica (Levey-Jennings, regras de Westgard) | `/mrquality/*` |
| **MRGuardian** | Monitoramento em tempo real (equipamentos, prazos, alarmes) | `/mrguardian/*` |
| **MRPooling** | Worklist / mapa de trabalho por posto/setor | `/mrpooling/*` |
| **MRInterface** | Integração com equipamentos (HL7 / ASTM) e sistemas externos (TISS, LIS de referência) | `/mrinterface/*` |

## Stack

- **Backend:** FastAPI (Python 3.12), SQLAlchemy 2.0, Alembic, PostgreSQL 16, Redis, JWT auth, multi-tenant por `tenant_id`
- **Frontend:** Next.js 15 (App Router), TypeScript, TailwindCSS, shadcn/ui, React Query
- **Infra:** Docker Compose para dev local; deploy alvo AWS/GCP/Fly.io
- **Integração:** hl7apy (HL7 v2), python-hl7, asyncpg

## Como rodar (dev local)

```bash
cp .env.example .env
docker compose up -d
```

- API: http://localhost:8000  •  docs: http://localhost:8000/docs
- Web: http://localhost:3000
- Postgres: localhost:5432 (usuário/senha em `.env`)

Rodar migrations:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.scripts.seed
```

Login inicial (após seed): `admin@demo.mr` / `mr123`.

## Estrutura

```
projeto lis/
├── backend/
│   ├── app/
│   │   ├── main.py           # entrypoint FastAPI
│   │   ├── core/             # config, security, dependencies
│   │   ├── models/           # SQLAlchemy models (multi-tenant)
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # rotas HTTP
│   │   └── modules/          # lógica de negócio por módulo MR*
│   └── alembic/              # migrations
├── frontend/
│   └── src/app/
│       ├── login/
│       └── (app)/
│           ├── mrlab/        # pacientes, médicos, requisições, coleta, agenda
│           ├── mrlablaudo/
│           ├── mrquality/
│           ├── mrguardian/
│           ├── mrpooling/
│           └── mrinterface/
└── docker-compose.yml
```

## Modelo comercial (SaaS)

- **Multi-tenant** — cada laboratório cliente é um `tenant`, isolamento por linha (`tenant_id`) em toda tabela.
- **Planos** — Starter (1 unidade), Pro (multi-unidade), Enterprise (SLA + integrações personalizadas).
- **Cobrança** — assinatura mensal por usuário ativo.

## Roadmap

- [x] Esqueleto de todos os 6 módulos
- [x] Auth JWT multi-tenant
- [x] CRUD pacientes, médicos, convênios, exames, requisições
- [ ] Assinatura digital de laudo (ICP-Brasil)
- [ ] Integração HL7 real com equipamentos (Cobas, Architect, Sysmex)
- [ ] TISS 4.x (envio de guias / lote XML)
- [ ] LGPD — pipeline de anonimização e trilha de auditoria
- [ ] Portal do paciente (app mobile React Native)
- [ ] Portal do médico solicitante
