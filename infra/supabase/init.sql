-- Supabase SQL Migration: Request Logs and Usage Tables
-- Run this in the Supabase SQL Editor to initialize the database schema.

-- 1. Create request_logs table
-- Stores metadata and status for each generation request.
CREATE TABLE IF NOT EXISTS request_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NULL,
    prompt TEXT NOT NULL,
    model TEXT NOT NULL,
    stream BOOLEAN DEFAULT FALSE,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'done', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ NULL,
    partial_output TEXT NULL
);

-- Comment explaining the table
COMMENT ON TABLE request_logs IS 'Tracks all generation requests, their status, and outputs.';

-- 2. Create usage table
-- Stores token usage and cost metrics for completed requests.
CREATE TABLE IF NOT EXISTS usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES request_logs(id) ON DELETE CASCADE,
    tokens INTEGER,
    cost NUMERIC(12, 6),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Comment explaining the table
COMMENT ON TABLE usage IS 'Tracks token usage and calculated cost for requests.';

-- Example Insert Statements (for testing):
-- INSERT INTO request_logs (prompt, model, status) VALUES ('Hello world', 'claude-3.5', 'queued');
-- INSERT INTO usage (request_id, tokens, cost) VALUES ('<UUID>', 100, 0.002);
