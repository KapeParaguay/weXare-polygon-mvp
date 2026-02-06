from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://wexare:wexare@localhost:5432/wexare"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    privy_app_id: str = ""
    privy_app_secret: str = ""
    usdc_token_address: str = ""
    escrow_manager_address: str = ""
    dispute_manager_address: str = ""
    rpc_url: str = ""
    cooperative_withdrawal_address: str = ""
    indexer_poll_sec: int = 10
    indexer_start_block: int = 0


settings = Settings()
