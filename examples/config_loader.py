#!/usr/bin/env python3
"""Configuration loading patterns with Result types and validation."""

from dataclasses import dataclass
from typing import TypeVar

from goated import Err, Ok, Result
from goated.result import GoError
from goated.std import json, strconv, strings

T = TypeVar("T")


@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str
    max_connections: int = 10
    timeout_seconds: int = 30


@dataclass
class ServerConfig:
    host: str
    port: int
    debug: bool = False
    workers: int = 4


@dataclass
class AppConfig:
    server: ServerConfig
    database: DatabaseConfig
    log_level: str = "INFO"


def require_field(obj: dict, field: str) -> Result[str, GoError]:
    """Extract a required field from a dict."""
    value = obj.get(field)
    if value is None:
        return Err(GoError(f"missing required field: {field}"))
    return Ok(str(value))


def parse_int_field(obj: dict, field: str, default: int | None = None) -> Result[int, GoError]:
    """Parse an integer field with optional default."""
    value = obj.get(field)
    if value is None:
        if default is not None:
            return Ok(default)
        return Err(GoError(f"missing required field: {field}"))

    if isinstance(value, int):
        return Ok(value)

    result = strconv.Atoi(str(value))
    match result:
        case Ok(n):
            return Ok(n)
        case Err(e):
            return Err(GoError(f"invalid integer for {field}: {e}"))

    return Err(GoError("unreachable"))


def parse_bool_field(obj: dict, field: str, default: bool = False) -> bool:
    """Parse a boolean field with default."""
    value = obj.get(field)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return strings.ToLower(str(value)) in ("true", "1", "yes", "on")


def parse_database_config(obj: dict) -> Result[DatabaseConfig, GoError]:
    """Parse database configuration section."""
    db = obj.get("database")
    if not isinstance(db, dict):
        return Err(GoError("missing or invalid 'database' section"))

    match require_field(db, "host"):
        case Err(e):
            return Err(e)
        case Ok(host):
            pass

    match parse_int_field(db, "port"):
        case Err(e):
            return Err(e)
        case Ok(port):
            pass

    match require_field(db, "name"):
        case Err(e):
            return Err(e)
        case Ok(name):
            pass

    match require_field(db, "user"):
        case Err(e):
            return Err(e)
        case Ok(user):
            pass

    match require_field(db, "password"):
        case Err(e):
            return Err(e)
        case Ok(password):
            pass

    max_conn = parse_int_field(db, "max_connections", 10).unwrap_or(10)
    timeout = parse_int_field(db, "timeout_seconds", 30).unwrap_or(30)

    return Ok(
        DatabaseConfig(
            host=host,
            port=port,
            name=name,
            user=user,
            password=password,
            max_connections=max_conn,
            timeout_seconds=timeout,
        )
    )


def parse_server_config(obj: dict) -> Result[ServerConfig, GoError]:
    """Parse server configuration section."""
    srv = obj.get("server")
    if not isinstance(srv, dict):
        return Err(GoError("missing or invalid 'server' section"))

    match require_field(srv, "host"):
        case Err(e):
            return Err(e)
        case Ok(host):
            pass

    match parse_int_field(srv, "port"):
        case Err(e):
            return Err(e)
        case Ok(port):
            pass

    debug = parse_bool_field(srv, "debug", False)
    workers = parse_int_field(srv, "workers", 4).unwrap_or(4)

    return Ok(
        ServerConfig(
            host=host,
            port=port,
            debug=debug,
            workers=workers,
        )
    )


def load_config(config_json: bytes) -> Result[AppConfig, GoError]:
    """Load and validate application configuration from JSON."""
    parsed = json.Unmarshal(config_json)

    match parsed:
        case Err(e):
            return Err(e)
        case Ok(obj):
            pass

    if not isinstance(obj, dict):
        return Err(GoError("config must be a JSON object"))

    match parse_server_config(obj):
        case Err(e):
            return Err(e)
        case Ok(server):
            pass

    match parse_database_config(obj):
        case Err(e):
            return Err(e)
        case Ok(database):
            pass

    log_level = str(obj.get("log_level", "INFO"))
    valid_levels = ["DEBUG", "INFO", "WARN", "ERROR"]
    if strings.ToUpper(log_level) not in valid_levels:
        return Err(GoError(f"invalid log_level: {log_level}"))

    return Ok(
        AppConfig(
            server=server,
            database=database,
            log_level=strings.ToUpper(log_level),
        )
    )


def main():
    print("=== Config Loader Example ===\n")

    valid_config = b"""{
        "server": {
            "host": "0.0.0.0",
            "port": 8080,
            "debug": true,
            "workers": 8
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp",
            "user": "admin",
            "password": "secret123",
            "max_connections": 20
        },
        "log_level": "debug"
    }"""

    print("=== Loading valid config ===")
    match load_config(valid_config):
        case Ok(config):
            print(f"Server: {config.server.host}:{config.server.port}")
            print(f"  Debug: {config.server.debug}, Workers: {config.server.workers}")
            print(f"Database: {config.database.host}:{config.database.port}/{config.database.name}")
            print(f"  Max connections: {config.database.max_connections}")
            print(f"Log level: {config.log_level}")
        case Err(e):
            print(f"Error: {e}")

    print("\n=== Loading config with missing field ===")
    bad_config = b"""{
        "server": {
            "host": "0.0.0.0"
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp",
            "user": "admin",
            "password": "secret"
        }
    }"""

    match load_config(bad_config):
        case Ok(config):
            print(f"Loaded: {config}")
        case Err(e):
            print(f"Expected error: {e}")

    print("\n=== Loading invalid JSON ===")
    match load_config(b"not valid json"):
        case Ok(_):
            print("Unexpected success")
        case Err(e):
            print(f"Expected error: {e}")


if __name__ == "__main__":
    main()
