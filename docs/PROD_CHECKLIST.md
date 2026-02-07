# Producción — Checklist de verificación rápida

## Requisitos previos
- `cast` (Foundry) instalado
- Variables de entorno cargadas en la terminal

## Variables requeridas
```
RPC_URL
CHAIN_ID
ESCROW_MANAGER_ADDRESS
DISPUTE_MANAGER_ADDRESS
USDC_TOKEN_ADDRESS
PRIVY_WALLET_ADDRESS
```

Opcionales si querés validar balance USDC:
```
USDC_DECIMALS=6
```

## 1) Verificar RPC y cadena
```
cast chain-id --rpc-url $RPC_URL
```
Debe devolver `137` (Polygon mainnet) o la red esperada.

## 2) Verificar roles del operador
```
cast call $ESCROW_MANAGER_ADDRESS \
  "hasRole(bytes32,address)(bool)" \
  $(cast keccak "OPERATOR_ROLE") \
  $PRIVY_WALLET_ADDRESS \
  --rpc-url $RPC_URL

cast call $DISPUTE_MANAGER_ADDRESS \
  "hasRole(bytes32,address)(bool)" \
  $(cast keccak "OPERATOR_ROLE") \
  $PRIVY_WALLET_ADDRESS \
  --rpc-url $RPC_URL
```
Debe devolver `true` en ambos.

## 3) Verificar balances
### MATIC
```
cast balance $PRIVY_WALLET_ADDRESS --rpc-url $RPC_URL
```
Debe ser > 0.

### USDC
```
cast call $USDC_TOKEN_ADDRESS \
  "balanceOf(address)(uint256)" \
  $PRIVY_WALLET_ADDRESS \
  --rpc-url $RPC_URL
```
Dividir entre `10^6` para ver USDC.

## 4) Verificar contratos accesibles
```
cast code $ESCROW_MANAGER_ADDRESS --rpc-url $RPC_URL | head
cast code $DISPUTE_MANAGER_ADDRESS --rpc-url $RPC_URL | head
```
Debe devolver bytecode (no vacío).

---

# Script rápido (si querés automatizar)
Podés usar `scripts/verify_prod.sh`.
