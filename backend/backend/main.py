import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from backend import create_app

env_path = sys.argv[1] if len(sys.argv) > 1 else None
if env_path:
    print(f"Loading environment variables from {env_path}")
    load_dotenv(env_path)

BASE_DIR = Path(__file__).resolve().parent
APP_MODE = os.getenv('APP_MODE', 'development')

CONFIG_BY_MODE = {
    'development': BASE_DIR / 'config.py',
    # Reuse integration test config when running backend against frontend integration scenarios.
    'frontend_integration': BASE_DIR.parent / 'test' / 'integration_test' / 'test_config.py',
}

config_path = os.getenv('APP_CONFIG_PATH')
if not config_path:
    config_path = str(CONFIG_BY_MODE.get(
        APP_MODE, CONFIG_BY_MODE['development']))

app = create_app(config=config_path)


def _resolve_ssl_context():
    if os.getenv('HTTPS_ENABLED', '0') != '1':
        return None

    cert_file = os.getenv('HTTPS_CERT_FILE')
    key_file = os.getenv('HTTPS_KEY_FILE')
    if cert_file and key_file:
        return cert_file, key_file
    if cert_file or key_file:
        raise ValueError(
            'HTTPS_CERT_FILE and HTTPS_KEY_FILE must both be set when using certificate-based HTTPS.')

    return os.getenv('HTTPS_SSL_CONTEXT', 'adhoc')


if __name__ == '__main__':
    run_kwargs = {
        'port': int(os.getenv('PORT', '5000')),
        'debug': os.getenv('FLASK_DEBUG', '1') == '1',
        'host': os.getenv('HOST', '0.0.0.0'),
    }

    ssl_context = _resolve_ssl_context()
    if ssl_context is not None:
        run_kwargs['ssl_context'] = ssl_context

    app.run(**run_kwargs)
