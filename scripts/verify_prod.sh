#!/usr/bin/env bash
set -euo pipefail

required=(RPC_URL CHAIN_ID ESCROW_MANAGER_ADDRESS DISPUTE_MANAGER_ADDRESS USDC_TOKEN_ADDRESS PRIVY_WALLET_ADDRESS)
for v in "${required[@]}"; do
  if [ -z "${!v:-}" ]; then
    echo "Missing env: $v" >&2
    exit 1
  fi
done

echo "== Chain ID =="
cast chain-id --rpc-url "$RPC_URL"

echo "== OPERATOR_ROLE (Escrow) =="
cast call "$ESCROW_MANAGER_ADDRESS" \
  "hasRole(bytes32,address)(bool)" \
  "$(cast keccak OPERATOR_ROLE)" \
  "$PRIVY_WALLET_ADDRESS" \
  --rpc-url "$RPC_URL"

echo "== OPERATOR_ROLE (Dispute) =="
cast call "$DISPUTE_MANAGER_ADDRESS" \
  "hasRole(bytes32,address)(bool)" \
  "$(cast keccak OPERATOR_ROLE)" \
  "$PRIVY_WALLET_ADDRESS" \
  --rpc-url "$RPC_URL"

echo "== MATIC balance =="
cast balance "$PRIVY_WALLET_ADDRESS" --rpc-url "$RPC_URL"

echo "== USDC balance =="
cast call "$USDC_TOKEN_ADDRESS" \
  "balanceOf(address)(uint256)" \
  "$PRIVY_WALLET_ADDRESS" \
  --rpc-url "$RPC_URL"

echo "== Contract bytecode =="
cast code "$ESCROW_MANAGER_ADDRESS" --rpc-url "$RPC_URL" | head -c 10; echo
cast code "$DISPUTE_MANAGER_ADDRESS" --rpc-url "$RPC_URL" | head -c 10; echo

echo "OK"
