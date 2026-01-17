import pytest
from unittest.mock import patch
import database
from database import Database

@pytest.fixture(autouse=True)
def reset_singleton():
    # clean up before test
    database.Database._Database__db = None
    database.Database._Database__instance = None
    yield # do the test
    # clean up after test
    database.Database._Database__db = None
    database.Database._Database__instance = None

def test_get_db_instance_creates_singleton_and_calls_sqlalchemy_once():
    with patch('database.SQLAlchemy') as mock_sqlalchemy: # patch the SQLAlchemy class used for db creation
        mock_sqlalchemy.return_value = 'db_object'
        app1 = object()
        inst1 = Database.get_db_instance(app1)
        inst2 = Database.get_db_instance(object())  # different app but should return same instance
        assert inst1 is inst2
        mock_sqlalchemy.assert_called_once_with(app1)
        assert database.Database._Database__db == 'db_object'

def test_direct_init_raises_if_db_already_set():
    with patch('database.SQLAlchemy') as mock_sqlalchemy:
        mock_sqlalchemy.return_value = 'db_object'
        Database.get_db_instance(object())
        # direct construction should raise the singleton exception
        with pytest.raises(Exception) as exc:
            Database(object())
        assert exc.value.args[0] == "This class is a singleton!"
