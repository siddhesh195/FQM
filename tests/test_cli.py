import os
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

import app.cli
from app.cli import interface


@pytest.mark.skipif(
    bool(os.getenv('DOCKER')),
    reason='Not supported in docker setup',
)
def test_cli_start(monkeypatch):
   

    runner = CliRunner()
    port = '8888'
    ip = '0.0.0.0'
    mock_bundle_app = MagicMock()
  
    mock_user = MagicMock()

    monkeypatch.setattr(app.cli, 'bundle_app', mock_bundle_app)
    
    monkeypatch.setattr(app.cli, 'User', mock_user)
    runner.invoke(interface, ['--cli', '--port', port, '--ip', ip, '--quiet'])

    mock_bundle_app().config['QUIET'] is True
    mock_bundle_app().config['CLI_OR_DEPLOY'] is True
    mock_bundle_app().config['LOCALADDR'] == ip


def test_cli_reset_password(monkeypatch):
    runner = CliRunner()
    mock_bundle_app = MagicMock()
    mock_user = MagicMock()

    monkeypatch.setattr(app.cli, 'bundle_app', mock_bundle_app)
    monkeypatch.setattr(app.cli, 'User', mock_user)
    runner.invoke(interface, ['--cli', '--reset'])

    mock_user.reset_default_password.assert_called_once_with()


def test_gui_start(monkeypatch):
    runner = CliRunner()
    mock_bundle_app = MagicMock()
    mock_app = MagicMock()
    mock_socketio = MagicMock()
    mock_bundle_app.return_value = (mock_app, mock_socketio)
    mock_import = MagicMock()
    mock_sys = MagicMock()

    monkeypatch.setattr(app.cli, 'bundle_app', mock_bundle_app)
    monkeypatch.setattr(app.cli, 'import_module', mock_import)
    monkeypatch.setattr(app.cli, 'sys', mock_sys)
    runner.invoke(interface, [])

    mock_bundle_app()[0].config['CLI_OR_DEPLOY'] is False
    mock_import().QApplication.assert_called_once_with(mock_sys.argv)
    mock_import().MainWindow.assert_called_once_with(mock_bundle_app()[0])
    mock_import().QCoreApplication.processEvents.assert_called_once_with()
    mock_import().QApplication().exec_.assert_called_once_with()


@pytest.mark.skipif(
    bool(os.getenv('DOCKER')),
    reason='Not supported in docker setup',
)
def test_gui_cli_fallback(monkeypatch):
  

    runner = CliRunner()
    mock_bundle_app = MagicMock()
    mock_sys = MagicMock()
  
    mock_monkey = MagicMock()

    def mock_import():
        raise AttributeError()

    monkeypatch.setattr(app.cli, 'bundle_app', mock_bundle_app)
    monkeypatch.setattr(app.cli, 'import_module', mock_import)
    monkeypatch.setattr(app.cli, 'sys', mock_sys)
   
    runner.invoke(interface, [])

    mock_bundle_app().config['QUIET'] is True
    mock_bundle_app().config['CLI_OR_DEPLOY'] is True
  
