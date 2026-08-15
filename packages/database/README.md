# @miracle-birds/database

Shared database utilities for Miracle Birds services.

## Contents

- `migrations/` — Shared Alembic migration utilities
- `schemas/` — Common SQL schema definitions

## Usage

All Python services reference the PostgreSQL connection via their own `app/core/database.py`.
This package holds shared SQL constants, migration helpers, and seed data scripts.
