# Deploy MR LIS — Grátis para sempre

Objetivo: subir o MR LIS na internet com URLs profissionais permanentes, **sem gastar nada**.

**Resultado final:**
- Frontend: `https://mr-lis.vercel.app`
- Backend: `https://mr-lis-api.fly.dev`
- Banco: PostgreSQL na Neon (3 GB grátis, para sempre)

Se quiser, depois, adicionar `mrlis.com.br` próprio: 5 minutos de CNAME no Vercel.

Tempo total: ~30 minutos de setup na primeira vez.

---

## 1. Banco de dados — Neon.tech

1. Vá em https://console.neon.tech e faça login (grátis, com Google/GitHub).
2. Clique **Create Project**:
   - Project name: `mr-lis`
   - Postgres version: 16 (padrão)
   - Region: **AWS us-east-1** (mais próximo de São Paulo com free)
3. Depois de criado, copie a **Connection string** do dashboard (opção *Pooled connection*).
   Formato: `postgresql://neondb_owner:xxxxxx@ep-xxx-pooler.us-east-1.aws.neon.tech/neondb`
4. Guarde essa URL — vai usar no passo 2.

---

## 2. Backend — Fly.io

### 2.1. Criar conta e instalar CLI

```powershell
# Windows PowerShell (admin)
iwr https://fly.io/install.ps1 -useb | iex
# fecha e reabre o PowerShell
fly version   # deve responder com a versão
fly auth signup   # (ou `fly auth login` se já tiver)
```

Fly.io pede cartão de crédito no signup, mas **não cobra** dentro do free allowance (2 VMs shared-cpu-1x + 3 GB storage).

### 2.2. Deploy do backend

```powershell
cd "D:\projeto lis\backend"
fly launch --copy-config --no-deploy
# Aceite: use existing app config (o fly.toml já está pronto)
# App name: mr-lis-api  (se disponível, senão escolha outro nome)
# Region: gru  (São Paulo — já está no fly.toml)
# Postgres? NÃO (usaremos Neon)
# Redis? NÃO
```

### 2.3. Configurar secrets

Cole a URL da Neon do passo 1 e gere uma SECRET_KEY:

```powershell
fly secrets set `
  DATABASE_URL="postgresql://neondb_owner:xxxxxx@ep-xxx-pooler.us-east-1.aws.neon.tech/neondb" `
  SECRET_KEY="$(python -c ""import secrets; print(secrets.token_urlsafe(48))"")" `
  CORS_ORIGINS="https://mr-lis.vercel.app,https://mr-lis-*.vercel.app"
```

### 2.4. Subir

```powershell
fly deploy
```

Isso monta o Docker, faz push, cria migrations no Neon e sobe o backend. Ao final:

```powershell
fly open   # abre https://mr-lis-api.fly.dev/docs no navegador
```

Se o `/docs` do FastAPI aparecer com todas as rotas, deu certo. Anote a URL final (vai usar no frontend).

### 2.5. Comandos úteis

```powershell
fly logs                       # logs em tempo real
fly status                     # status da app
fly ssh console                # shell dentro do container
fly scale count 1              # garante 1 máquina rodando (evita cold start)
```

---

## 3. Frontend — Vercel

### 3.1. Criar conta e instalar CLI

```powershell
npm install -g vercel
vercel login   # abre o navegador para autenticar (email/GitHub/Google)
```

### 3.2. Deploy

```powershell
cd "D:\projeto lis\frontend"
vercel
# Perguntas:
# - Set up and deploy? Yes
# - Which scope? (sua conta pessoal)
# - Link to existing project? No
# - Project name? mr-lis
# - In which directory is your code located? ./  (default)
# - Want to modify the settings? No
```

Vai fazer um deploy preview inicial.

### 3.3. Configurar variável BACKEND_URL

```powershell
vercel env add BACKEND_URL production
# Cole: https://mr-lis-api.fly.dev  (a URL do passo 2.4)

vercel env add BACKEND_URL preview
# Cole a mesma URL

vercel env add BACKEND_URL development
# Cole: http://localhost:8000
```

### 3.4. Deploy final em produção

```powershell
vercel --prod
```

Ao terminar, Vercel mostra a URL: `https://mr-lis.vercel.app` (ou variação).

**Acesse essa URL no navegador**. Login: `admin@demo.mr` / senha `mr123` / tenant `demo`.

---

## 4. (Opcional) Domínio próprio no futuro

Quando comprar `mrlis.com.br` (Registro.br, ~R$40/ano) ou `.com` (Cloudflare Registrar, ~USD 10/ano):

### 4.1. No painel Vercel
- Vá em `mr-lis` → Settings → Domains
- Add domain: `mrlis.com.br` (ou `app.mrlis.com.br`)
- Vercel mostra os registros DNS que você precisa criar.

### 4.2. No painel do registrar (Registro.br / Cloudflare)
- Crie um registro **CNAME** apontando `app.mrlis.com.br` → `cname.vercel-dns.com`
- Ou registro **A** para apex (`mrlis.com.br`) → IP fornecido pelo Vercel

### 4.3. Atualizar CORS no backend
```powershell
cd "D:\projeto lis\backend"
fly secrets set CORS_ORIGINS="https://app.mrlis.com.br,https://mrlis.com.br,https://mr-lis.vercel.app"
```

Propagação DNS: 5 min a 2 h. HTTPS automático (Vercel emite Let's Encrypt).

---

## 5. Manutenção

**Atualizar código:**
```powershell
# Frontend
cd "D:\projeto lis\frontend"
vercel --prod

# Backend
cd "D:\projeto lis\backend"
fly deploy
```

**Ver logs:**
- Vercel: `vercel logs` ou dashboard web
- Fly.io: `fly logs`
- Neon: dashboard web (Monitoring)

**Backup do banco (Neon):**
- Dashboard Neon → Branches → Create branch → snapshot instantâneo

---

## 6. Limites do free tier

| Recurso | Limite | O que acontece se estourar |
|---|---|---|
| **Vercel** | 100 GB banda/mês, builds ilimitados | Precisa upgrade ($20/mês Pro) |
| **Fly.io** | 2 VMs shared-cpu-1x, 3 GB storage | Cobra proporcional ($1.94/GB extra) |
| **Neon** | 3 GB storage, 100 h compute/mês | Suspende connections até virar mês |

Para 100-500 usuários ativos, tudo dentro do free tier. A partir daí, upgrade custa ~USD 25/mês (Vercel Pro + Fly hobby + Neon Launch).

---

## 7. Troubleshooting

**`fly deploy` erro "app not found":**
- Rode `fly apps list` — se `mr-lis-api` já foi pego, edite `app = ...` no `fly.toml` pra outro nome.

**Frontend abre mas login dá "Failed to fetch":**
- Verifique `vercel env ls` — `BACKEND_URL` precisa estar setada em `production`.
- Rode `curl https://mr-lis-api.fly.dev/health` — se não responder 200, o backend caiu.

**Backend responde mas login retorna 500:**
- `fly logs` — provavelmente `DATABASE_URL` errada ou Neon suspendida.
- Vá no Neon dashboard, clique em "Resume compute" se estiver ocioso.

**Sistema lento no primeiro acesso:**
- Fly.io `auto_stop_machines = "stop"` desliga a VM quando ninguém acessa. Primeiro request após 5 min ocioso demora ~5-10s (cold start).
- Pra evitar: `fly scale count 1` e edite `fly.toml` para `min_machines_running = 1` (aí gasta mais free credit).
