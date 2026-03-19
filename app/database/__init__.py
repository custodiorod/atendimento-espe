"""Database module for Supabase integration."""

from app.database.supabase import get_supabase, supabase_client

__all__ = ["get_supabase", "supabase_client"]
