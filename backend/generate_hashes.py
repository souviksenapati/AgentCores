#!/usr/bin/env python3
"""Generate password hashes for demo users"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

passwords = {
    "owner123": pwd_context.hash("owner123"),
    "admin123": pwd_context.hash("admin123"),
    "developer123": pwd_context.hash("developer123"),
    "manager123": pwd_context.hash("manager123"),
    "analyst123": pwd_context.hash("analyst123"),
    "operator123": pwd_context.hash("operator123"),
    "viewer123": pwd_context.hash("viewer123"),
    "guest123": pwd_context.hash("guest123"),
}

print("Password hashes for demo users:")
for password, hash_value in passwords.items():
    print(f"{password}: {hash_value}")
