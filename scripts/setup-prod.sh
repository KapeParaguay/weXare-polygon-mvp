#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required_vars=(
  DATABASE_URL
  SUPABASE_URL
  SUPABASE_ANON_KEY
  SUPABASE_SERVICE_ROLE_KEY
  PRIVY_APP_ID
  PRIVY_APP_SECRET
  PRIVY_VERIFICATION_KEY
  PRIVY_AUTH_KEY
  PRIVY_WALLET_ID
  PRIVY_WALLET_ADDRESS
  RPC_URL
  CHAIN_ID
  USDC_TOKEN_ADDRESS
  ESCROW_MANAGER_ADDRESS
  DISPUTE_MANAGER_ADDRESS
  COOP_WALLET_ADDRESS
)

echo "Checking required environment variables..."
missing=0
for v in "${required_vars[@]}"; do
  if [[ -z "${!v:-}" ]]; then
    echo "  - MISSING: $v"
    missing=1
  fi
done

if [[ "$missing" -eq 1 ]]; then
  echo ""
  echo "Set the missing variables in backend/.env or your deploy environment."
  exit 1
fi

echo ""
echo "Running migrations..."
cd "$ROOT_DIR/backend"
alembic upgrade head

echo ""
echo "Done. Next steps:"
echo "1) Verify OPERATOR_ROLE on-chain (see docs/PROD_CHECKLIST.md)."
echo "2) Ensure MATIC/USDC funded in PRIVY_WALLET_ADDRESS."
