## Local HTTPS testing

The backend can be started with HTTPS for local verification before deployment.

Ad hoc certificate mode:

```bash
HTTPS_ENABLED=1 HTTPS_SSL_CONTEXT=adhoc uv run -m backend.main ./test/integration_test/.env_frontend_integration
```

Custom certificate mode:

```bash
HTTPS_ENABLED=1 HTTPS_CERT_FILE=/path/to/cert.pem HTTPS_KEY_FILE=/path/to/key.pem uv run -m backend.main ./test/integration_test/.env_frontend_integration
```

Keep HTTPS disabled by default unless you are explicitly testing TLS locally.
