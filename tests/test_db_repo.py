import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from src.app.db import SupabaseClientWrapper
from src.app.repos.request_repo import RequestRepo

class FakeSupabaseClient:
    """
    Fake client that mimics the Supabase client interface for testing.
    """
    def __init__(self):
        self.table_mock = MagicMock()
        self.insert_mock = MagicMock()
        self.update_mock = MagicMock()
        self.select_mock = MagicMock()
        self.eq_mock = MagicMock()
        self.execute_mock = MagicMock()

        # Chain setup
        self.table_mock.return_value = self
        self.insert_mock.return_value = self
        self.update_mock.return_value = self
        self.select_mock.return_value = self
        self.eq_mock.return_value = self
        self.execute_mock.return_value = self

    def table(self, name):
        self.table_mock(name)
        return self

    def insert(self, data):
        self.insert_mock(data)
        # Return predictable data
        self.execute_mock.return_value.data = [{"id": "test-id", "created_at": "now"}]
        return self

    def update(self, data):
        self.update_mock(data)
        self.execute_mock.return_value.data = [{"id": "test-id", "status": data.get("status")}]
        return self
    
    def select(self, columns):
        self.select_mock(columns)
        return self

    def eq(self, column, value):
        self.eq_mock(column, value)
        return self

    def execute(self):
        return self.execute_mock()

def test_create_request():
    fake_client = FakeSupabaseClient()
    db = SupabaseClientWrapper("url", "key", client=fake_client)
    repo = RequestRepo(db)

    result = repo.create_request("prompt", "model", False)
    
    assert result["id"] == "test-id"
    fake_client.table_mock.assert_called_with("request_logs")
    fake_client.insert_mock.assert_called()

def test_set_done():
    fake_client = FakeSupabaseClient()
    db = SupabaseClientWrapper("url", "key", client=fake_client)
    repo = RequestRepo(db)

    repo.set_done("test-id", "output")
    
    fake_client.table_mock.assert_called_with("request_logs")
    fake_client.update_mock.assert_called()
    # Verify update args contain status='done'
    args, _ = fake_client.update_mock.call_args
    assert args[0]["status"] == "done"
    assert args[0]["partial_output"] == "output"

def test_add_usage():
    fake_client = FakeSupabaseClient()
    db = SupabaseClientWrapper("url", "key", client=fake_client)
    repo = RequestRepo(db)

    repo.add_usage("test-id", 100, Decimal("0.002"))
    
    fake_client.table_mock.assert_called_with("usage")
    fake_client.insert_mock.assert_called()
    args, _ = fake_client.insert_mock.call_args
    assert args[0]["tokens"] == 100
    assert args[0]["cost"] == 0.002
