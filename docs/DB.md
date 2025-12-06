# Database Setup Guide

## Overview
This project uses Supabase (PostgreSQL) to store request logs and usage metrics.

## Schema
The database consists of two main tables:
1.  `request_logs`: Tracks every generation request, its status (queued, running, done, failed), and the generated output.
2.  `usage`: Tracks token consumption and cost for each request.

## Setup Instructions
1.  **Create a Supabase Project**: Go to [supabase.com](https://supabase.com) and create a new project.
2.  **Run Migration**:
    -   Go to the **SQL Editor** in your Supabase dashboard.
    -   Copy the contents of `infra/supabase/init.sql`.
    -   Paste and run the SQL script.
    -   Verify that `request_logs` and `usage` tables are created.

## Configuration
To connect the application to your Supabase instance:
1.  Get your **Project URL** and **API Key** (service_role key recommended for backend) from Supabase settings.
2.  Set them in your environment:
    -   **Local**: Add to `.env`:
        ```bash
        SUPABASE_URL=https://your-project.supabase.co
        SUPABASE_KEY=your-secret-key
        ```
    -   **Production**: Add to AWS Secrets Manager (see `docs/SECRETS.md`).

## Development Flow
-   **New Request**: App inserts a row into `request_logs` with status `queued`.
-   **Streaming**: App updates `partial_output` and sets status to `running`.
-   **Completion**: App sets status to `done` and inserts a row into `usage`.

## Testing
The application uses a wrapper around the Supabase client. In tests, we use a fake client to verify logic without connecting to the real database.
