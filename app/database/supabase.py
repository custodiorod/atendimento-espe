"""Supabase client singleton and utilities."""

from functools import lru_cache
from typing import Any, Optional

from supabase import Client, PostgrestClient, create_client
from supabase.lib.client_options import ClientOptions

from app.config import get_settings

settings = get_settings()


@lru_cache
def get_supabase() -> Client:
    """
    Get cached Supabase client instance.

    Returns:
        Supabase client

    Raises:
        ValueError: If Supabase is not configured
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("Supabase is not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")

    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
        options=ClientOptions(
            postgrest_client_timeout=30,
            storage_client_timeout=30,
        ),
    )


# Singleton instance
supabase_client: Optional[Client] = None


def init_supabase() -> Client:
    """
    Initialize Supabase client singleton.

    Returns:
        Supabase client
    """
    global supabase_client
    supabase_client = get_supabase()
    return supabase_client


class SupabaseRepository:
    """Base repository class for Supabase operations."""

    def __init__(self, table_name: str):
        """
        Initialize repository.

        Args:
            table_name: Name of the table in Supabase
        """
        self.table_name = table_name
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Get Supabase client."""
        if self._client is None:
            self._client = get_supabase()
        return self._client

    @property
    def table(self) -> PostgrestClient:
        """Get Supabase table reference."""
        return self.client.table(self.table_name)

    async def get_by_id(self, record_id: str) -> Optional[dict[str, Any]]:
        """
        Get record by ID.

        Args:
            record_id: Record UUID

        Returns:
            Record data or None if not found
        """
        response = self.table.select("*").eq("id", record_id).execute()
        if response.data:
            return response.data[0]
        return None

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Create new record.

        Args:
            data: Record data

        Returns:
            Created record
        """
        response = self.table.insert(data).execute()
        return response.data[0]

    async def update(self, record_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Update record by ID.

        Args:
            record_id: Record UUID
            data: Data to update

        Returns:
            Updated record or None if not found
        """
        response = self.table.update(data).eq("id", record_id).execute()
        if response.data:
            return response.data[0]
        return None

    async def delete(self, record_id: str) -> bool:
        """
        Delete record by ID.

        Args:
            record_id: Record UUID

        Returns:
            True if deleted, False if not found
        """
        response = self.table.delete().eq("id", record_id).execute()
        return len(response.data) > 0

    async def list_all(
        self,
        filters: Optional[dict[str, Any]] = None,
        order: str = "-created_at",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        List records with optional filters.

        Args:
            filters: Optional column filters
            order: Order by column (prefix with - for descending)
            limit: Maximum records to return

        Returns:
            List of records
        """
        query = self.table.select("*")

        # Apply filters
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)

        # Apply ordering
        if order.startswith("-"):
            query = query.order(order[1:], desc=True)
        else:
            query = query.order(order)

        # Apply limit
        query = query.limit(limit)

        response = query.execute()
        return response.data

    async def exists(self, **filters) -> bool:
        """
        Check if record exists matching filters.

        Args:
            **filters: Column filters

        Returns:
            True if record exists
        """
        response = self.table.select("id").limit(1)
        for column, value in filters.items():
            response = response.eq(column, value)

        response = response.execute()
        return len(response.data) > 0
