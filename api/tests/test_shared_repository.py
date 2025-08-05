import pytest
from unittest.mock import Mock
from app.shared.repository import BaseRepository


class TestBaseRepository:
    def test_init(self):
        mock_db = Mock()
        repo = BaseRepository(mock_db)
        assert repo.db == mock_db