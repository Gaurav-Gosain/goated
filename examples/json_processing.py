#!/usr/bin/env python3
"""JSON processing patterns with goated."""

from dataclasses import dataclass

from goated import Err, Ok, Result
from goated.result import GoError
from goated.std import json


@dataclass
class User:
    id: int
    name: str
    email: str
    active: bool = True


def parse_user(data: bytes) -> Result[User, GoError]:
    """Parse JSON bytes into a User object."""
    result = json.Unmarshal(data)

    match result:
        case Err(e):
            return Err(e)
        case Ok(obj):
            try:
                return Ok(
                    User(
                        id=obj["id"],
                        name=obj["name"],
                        email=obj["email"],
                        active=obj.get("active", True),
                    )
                )
            except (KeyError, TypeError) as e:
                return Err(GoError(str(e)))

    return Err(GoError("unreachable"))


def users_to_json(users: list[User]) -> str:
    """Convert list of users to JSON string."""
    data = [{"id": u.id, "name": u.name, "email": u.email, "active": u.active} for u in users]
    return json.MarshalIndent(data, "", "  ").unwrap_or("[]")


def main():
    print("=== JSON Processing Examples ===\n")

    raw = b'{"id": 1, "name": "Alice", "email": "alice@example.com"}'
    match parse_user(raw):
        case Ok(user):
            print(f"Parsed user: {user}")
        case Err(e):
            print(f"Parse error: {e}")

    bad_raw = b'{"id": 1, "name": "Bob"}'
    match parse_user(bad_raw):
        case Ok(user):
            print(f"Parsed user: {user}")
        case Err(e):
            print(f"Expected error for missing email: {e}")

    users = [
        User(1, "Alice", "alice@example.com"),
        User(2, "Bob", "bob@example.com", active=False),
        User(3, "Charlie", "charlie@example.com"),
    ]

    print("\nSerialized users:")
    print(users_to_json(users))

    print("\n=== Streaming JSON ===")
    json_lines = [
        b'{"event": "login", "user": "alice"}',
        b'{"event": "purchase", "user": "bob", "amount": 99.99}',
        b'{"event": "logout", "user": "alice"}',
    ]

    for line in json_lines:
        event = json.Unmarshal(line).unwrap()
        print(f"Event: {event['event']:10} | User: {event['user']}")


if __name__ == "__main__":
    main()
