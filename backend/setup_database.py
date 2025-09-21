#!/usr/bin/env python3
"""
Simple database setup script for AgentCores multi-tenant system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_database

if __name__ == "__main__":
    print("🚀 Setting up AgentCores multi-tenant database...")
    try:
        init_database()
        print("✅ Database setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start the backend server: uvicorn app.main:app --reload")
        print("2. Start the frontend: npm start")
        print("3. Login at http://localhost:3000 with admin@demo.agentcores.com / admin123")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)