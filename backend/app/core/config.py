from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://wexare:wexare@localhost:5432/wexare"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    privy_app_id: str = ""
    privy_app_secret: str = ""
    privy_verification_key: str = ""
    privy_issuer: str = ""
    privy_auth_key: str = ""
    privy_api_base: str = "https://api.privy.io"
    privy_wallet_id: str = ""
    privy_wallet_address: str = ""
    coop_wallet_address: str = ""
    chain_id: int = 137
    auth_allow_mock: bool = True
    moonpay_enabled: bool = True
    withdraw_external_enabled: bool = True
    default_withdraw_method: str = "moonpay"
    moonpay_fee_buffer_pct: float = 0.06
    moonpay_fee_buffer_min_usd: float = 3.0
    onchain_node_fee_usd: float = 0.25
    usdc_token_address: str = ""
    escrow_manager_address: str = ""
    dispute_manager_address: str = ""
    rpc_url: str = ""
    indexer_poll_sec: int = 10
    indexer_start_block: int = 0

    openai_api_key: str = ""
    openrouter_api_key: str = ""
    llm_provider_priority: str = "openai,openrouter"
    llm_model_openai: str = "gpt-4o-mini"
    llm_model_openrouter: str = "deepseek-chat"


settings = Settings()
