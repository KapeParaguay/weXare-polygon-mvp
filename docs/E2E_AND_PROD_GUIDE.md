# WEXARE MVP — Guía E2E (Local/Demo)

## Objetivo
Probar el flujo end‑to‑end **en UX Web2** (sin tocar contratos desde el frontend). El backend orquesta todo.

## Requisitos
- Docker Desktop (para `make dev`) o ejecución local de backend/frontend.
- Node 18+ y Python 3.12 si no usas Docker.
- Variables básicas en `.env` (ver abajo).

## 1) Configuración mínima (local)

### Backend `.env` mínimo
```
DATABASE_URL=postgresql+psycopg2://wexare:wexare@localhost:5432/wexare
AUTH_ALLOW_MOCK=true
MOONPAY_ENABLED=true
WITHDRAW_EXTERNAL_ENABLED=true
DEFAULT_WITHDRAW_METHOD=moonpay
MOONPAY_FEE_BUFFER_PCT=0.06
MOONPAY_FEE_BUFFER_MIN_USD=3
ONCHAIN_NODE_FEE_USD=0.25
```

### Frontend `.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 2) Levantar stack
```
make dev
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## 3) Flujo E2E (modo demo con mock funding)

### Paso 1: Fondear cuenta
- Ir a `/wallet/deposit`
- Ingresa monto
- Click **Start MoonPay**
- Luego **Mock confirm funding** (dev‑only)

Resultado esperado:
- Balance en Creator/Worker sube
- Se descuenta un fee fijo por cada quest fondeada (ONCHAIN_NODE_FEE_USD)

### Paso 2: Crear proyecto
- Ir a `/creator`
- Si balance > 0, se habilita **Create project**
- Completar título + descripción
- Se genera propuesta

### Paso 3: Ver propuesta
- Ir a `/creator/projects/:id/proposal`
- Validar presupuesto y buffer
- Click **Approve proposal** (se bloquea propuesta)

### Paso 4: Fondear quest
- Ir a `/creator/projects/:id`
- Click **Fund quest** (redirige a `/creator/fund?quest_id=`)
- Completar monto → **Start funding**
- Simular status (PAID_PENDING / CONFIRMED)
Nota: el balance debe cubrir `monto + ONCHAIN_NODE_FEE_USD`.

### Paso 5: Worker acepta tarea
- Ir a `/worker/feed`
- Aceptar tarea

### Paso 6: Worker entrega
- Ir a `/worker/tasks/active`
- Enviar evidencia

### Paso 7: Creator aprueba o disputa
- Ir a `/creator/quests/:id/review`
- **Approve** o **Dispute**

### Paso 8: Judge vota
- Ir a `/judge`
- Aceptar oferta
- Ir a `/judge/disputes/:id`
- Votar

### Paso 9: Retiro
- Ir a `/wallet/withdraw`
- Solicitar retiro

## 4) Checks rápidos
- `/creator` muestra balance real
- Botones no están “muertos”
- Disputas generan ofertas de juez

---

# WEXARE MVP — Guía de despliegue a Producción

## Objetivo
Desplegar plataforma completa con **transacciones reales** en Polygon.

## 0) Qué está listo y qué depende del deploy
Listo en el repo:
- Backend firma y envía transacciones con Privy.
- UX Web2 (sin MetaMask) con fondeo/retiro por MoonPay.
- Ledger interno y balance por usuario.
- Fee fijo por nodo (`ONCHAIN_NODE_FEE_USD`) para cubrir gas.

Depende del deploy:
- Variables de entorno reales.
- OPERATOR_ROLE on‑chain.
- Fondos de gas (MATIC) y USDC en la wallet operadora.
- Webhook público de MoonPay.

## 1) Variables de entorno obligatorias

### Backend (`backend/.env`)
```
DATABASE_URL=...
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...

PRIVY_APP_ID=...
PRIVY_APP_SECRET=...
PRIVY_VERIFICATION_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
PRIVY_AUTH_KEY=...   # Authorization key (Wallet infrastructure)
PRIVY_WALLET_ID=...  # ID del server wallet
PRIVY_WALLET_ADDRESS=...  # Address del server wallet

RPC_URL=https://polygon-rpc.com
CHAIN_ID=137
USDC_TOKEN_ADDRESS=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
ESCROW_MANAGER_ADDRESS=...
DISPUTE_MANAGER_ADDRESS=...
COOP_WALLET_ADDRESS=...

MOONPAY_ENABLED=true
WITHDRAW_EXTERNAL_ENABLED=true
DEFAULT_WITHDRAW_METHOD=moonpay
ONCHAIN_NODE_FEE_USD=0.25
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_URL=https://<backend-domain>
NEXT_PUBLIC_PRIVY_APP_ID=...
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

## 1.1) Cómo conseguir cada variable

### Base de datos
- `DATABASE_URL`: URL de tu Postgres (Supabase, RDS, Neon o local). En Supabase está en **Project Settings → Database → Connection string**.

### Supabase
- `SUPABASE_URL`: **Project Settings → API → Project URL**.
- `SUPABASE_ANON_KEY`: **Project Settings → API → anon key**.
- `SUPABASE_SERVICE_ROLE_KEY`: **Project Settings → API → service_role key**.

### Privy (Auth + Server Wallets)
En el dashboard de Privy:
- `PRIVY_APP_ID`: **App settings → Basics → App ID**.
- `PRIVY_APP_SECRET`: **App settings → Basics → App Secret**.
- `PRIVY_VERIFICATION_KEY`: **App settings → Basics → Verification Key** (pegar con `-----BEGIN/END PUBLIC KEY-----` y con `\\n` en `.env`).
- `PRIVY_AUTH_KEY`: **Wallet infrastructure → Authorization keys → Create key** (guardar la key, no se muestra de nuevo).
- `PRIVY_WALLET_ID`: **Wallet infrastructure → Wallets → Create new wallet** (copiar el ID).
- `PRIVY_WALLET_ADDRESS`: Address del wallet creado (misma pantalla).
Notas:
- Una wallet EVM sirve para todas las redes EVM (Polygon, Ethereum, etc.). La address es la misma.
- La red la determina el `CHAIN_ID` y el `RPC_URL`.

### Blockchain (Polygon)
- `RPC_URL`: endpoint RPC de Polygon (ej. `https://polygon-rpc.com` o proveedor como Alchemy/Infura).
- `CHAIN_ID`: `137` (Polygon mainnet) o `80002` (Amoy).
- `USDC_TOKEN_ADDRESS`:
  - Polygon mainnet: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`.
  - Amoy: usar la dirección oficial de USDC del testnet que estés usando.
- `ESCROW_MANAGER_ADDRESS`, `DISPUTE_MANAGER_ADDRESS`: direcciones de tus contratos ya desplegados.
- `COOP_WALLET_ADDRESS`: wallet receptora de pagos (payee on‑chain).
- `ONCHAIN_NODE_FEE_USD`: fee fijo por cada quest fondeada (recomendado `0.25`).

### MoonPay (si se usa real)
- `MOONPAY_ENABLED`: `true` para producción.
- Webhooks y claves de MoonPay dependen del setup real; si no está integrado, usar `false` y operar con mock.

## 2) Migraciones
```
cd backend
alembic upgrade head
```
O usar el script:
```
./scripts/setup-prod.sh
```

## 3) Dar OPERATOR_ROLE al wallet custodial
Necesitas la private key del deployer/admin del contrato.

```
cast send $ESCROW_MANAGER_ADDRESS \
  "grantRole(bytes32,address)" \
  $(cast keccak "OPERATOR_ROLE") \
  $PRIVY_WALLET_ADDRESS \
  --rpc-url $RPC_URL \
  --private-key $ADMIN_PRIVATE_KEY

cast send $DISPUTE_MANAGER_ADDRESS \
  "grantRole(bytes32,address)" \
  $(cast keccak "OPERATOR_ROLE") \
  $PRIVY_WALLET_ADDRESS \
  --rpc-url $RPC_URL \
  --private-key $ADMIN_PRIVATE_KEY
```

## 4) Fondos del wallet custodial
- Enviar **MATIC** (gas)
- Enviar **USDC** (fondos para escrow)
Nota: el backend descuenta `ONCHAIN_NODE_FEE_USD` por quest fondeada para cubrir gas.

## 5) Confirmar indexer
El indexer corre dentro del backend si existen:
- `RPC_URL`
- `ESCROW_MANAGER_ADDRESS`
- `DISPUTE_MANAGER_ADDRESS`

## 6) Webhook MoonPay (producción)
Configurar el endpoint público:
- `POST /webhooks/moonpay` (backend)
- La firma se valida con `MOONPAY_WEBHOOK_SECRET`

## 7) Validación final antes de prod
Usar `docs/PROD_CHECKLIST.md` o el script:
```
./scripts/verify_prod.sh
```

## 8) Flujo de deploy recomendado
1. Configurar `.env` en backend y `.env.local` en frontend.
2. Correr `./scripts/setup-prod.sh`.
3. Otorgar `OPERATOR_ROLE` on‑chain.
4. Fondear wallet custodial con MATIC/USDC.
5. Configurar webhook MoonPay.
6. Validar con `scripts/verify_prod.sh`.

## 6) Validación rápida en prod
- Crear proyecto
- Fondear
- Aprobar
- Disputar
- Votar
- Ver balances

## 7) Checklist y script de verificación
- Checklist: `docs/PROD_CHECKLIST.md`
- Script: `scripts/verify_prod.sh`

---

## Notas críticas
- Sin `PRIVY_AUTH_KEY` no hay firma real.
- Sin `OPERATOR_ROLE` las tx revierten.
- Sin MATIC el wallet no puede pagar gas.
