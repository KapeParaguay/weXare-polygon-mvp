-- Generated schema for MVP (Postgres)
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  wallet_address TEXT UNIQUE,
  status TEXT NOT NULL,
  roles TEXT NOT NULL
);

CREATE TABLE worker_profiles (
  id SERIAL PRIMARY KEY,
  user_id TEXT,
  skills TEXT[],
  pricing FLOAT,
  scores FLOAT,
  active_task_id INT
);

CREATE TABLE judge_profiles (
  id SERIAL PRIMARY KEY,
  user_id TEXT,
  judge_score FLOAT,
  acceptance_rate FLOAT,
  cooldown INT
);

CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  creator_id TEXT,
  title TEXT,
  description TEXT
);

CREATE TABLE proposals (
  id SERIAL PRIMARY KEY,
  project_id INT,
  version INT,
  locked BOOLEAN,
  data JSONB
);

CREATE TABLE quests (
  id SERIAL PRIMARY KEY,
  project_id INT,
  parent_quest_id INT,
  index INT,
  scope_hash TEXT,
  budget FLOAT,
  status TEXT,
  funded_at TIMESTAMP
);

CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  quest_id INT,
  type TEXT,
  status TEXT,
  assigned_user_id TEXT
);

CREATE TABLE task_declines (
  id SERIAL PRIMARY KEY,
  task_id INT,
  user_id TEXT,
  declined_at TIMESTAMP
);

CREATE TABLE evidence (
  id SERIAL PRIMARY KEY,
  owner_id TEXT,
  task_id INT,
  quest_id INT,
  url TEXT,
  type TEXT
);

CREATE TABLE disputes (
  id SERIAL PRIMARY KEY,
  status TEXT,
  quest_id INT,
  opened_by TEXT,
  reason TEXT,
  evidence TEXT
);

CREATE TABLE judge_offers (
  id SERIAL PRIMARY KEY,
  dispute_id INT,
  judge_user_id TEXT,
  status TEXT,
  expires_at TIMESTAMP,
  accepted_at TIMESTAMP
);

CREATE TABLE judge_votes (
  id SERIAL PRIMARY KEY,
  dispute_id INT,
  judge_user_id TEXT,
  vote TEXT,
  split INT,
  comment TEXT
);

CREATE TABLE escrow_ledger (
  id SERIAL PRIMARY KEY,
  quest_id INT,
  user_id TEXT,
  kind TEXT,
  onchain_tx TEXT,
  amount FLOAT,
  status TEXT,
  created_at TIMESTAMP
);

CREATE TABLE payments (
  id SERIAL PRIMARY KEY,
  creator_id TEXT,
  quest_id INT,
  amount FLOAT,
  fee FLOAT,
  status TEXT,
  provider TEXT,
  created_at TIMESTAMP
);

CREATE TABLE withdrawals (
  id SERIAL PRIMARY KEY,
  user_id TEXT,
  amount FLOAT,
  method TEXT,
  destination TEXT,
  country TEXT,
  status TEXT,
  coop_tx TEXT,
  created_at TIMESTAMP
);

CREATE TABLE experience_records (
  id SERIAL PRIMARY KEY,
  user_id TEXT,
  quest_id INT,
  role TEXT,
  outcome TEXT,
  was_disputed BOOLEAN,
  dispute_result TEXT,
  executor_type TEXT,
  created_at TIMESTAMP
);

CREATE TABLE indexer_state (
  id SERIAL PRIMARY KEY,
  key TEXT UNIQUE,
  value TEXT
);

CREATE TABLE reputation_logs (
  id SERIAL PRIMARY KEY,
  user_id TEXT,
  role TEXT,
  previous_score FLOAT,
  new_score FLOAT,
  formula_version TEXT,
  created_at TIMESTAMP
);

CREATE TABLE task_offers (
  id SERIAL PRIMARY KEY,
  task_id INT,
  worker_id TEXT,
  status TEXT,
  expires_at TIMESTAMP
);

CREATE TABLE skill_runs (
  id SERIAL PRIMARY KEY,
  quest_id INT,
  skill_type TEXT,
  status TEXT,
  artifact_url TEXT,
  created_at TIMESTAMP
);

CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  actor_id TEXT,
  action TEXT,
  details TEXT,
  created_at TIMESTAMP
);
