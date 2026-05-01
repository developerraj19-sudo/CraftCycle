"""
sync_db.py — Database schema synchronisation script.
Run this once after deployment to fix schema mismatches.

Handles:
- Creating missing tables
- Adding missing columns
- Converting PostgreSQL ENUM columns to VARCHAR (fixes 500 on INSERT)
"""
from app import create_app
from extensions import db
from sqlalchemy import text
import sys

app = create_app()

with app.app_context():
    print("=" * 60)
    print("  CraftCycle DB Sync")
    print("=" * 60)

    # ── 1. Create all tables that don't exist yet ──────────────
    print("\n[1] Creating tables (create_all)...")
    try:
        db.create_all()
        print("    OK")
    except Exception as e:
        print(f"    ERROR: {e}")
        sys.exit(1)

    # ── 2. Fix ENUM → VARCHAR on the 'orders' table ────────────
    # PostgreSQL creates native ENUM types when SQLAlchemy uses db.Enum().
    # These are strict and cause "invalid input value for enum" on INSERT.
    # We convert them to plain VARCHAR using USING clause.
    print("\n[2] Converting ENUM columns to VARCHAR on 'orders'...")
    enum_conversions = [
        ("orders",      "status",         "VARCHAR(20)",  "'pending'"),
        ("orders",      "payment_status", "VARCHAR(20)",  "'pending'"),
        ("scrap_materials", "status",     "VARCHAR(20)",  "'active'"),
        ("products",    "status",         "VARCHAR(20)",  "'active'"),
    ]
    for table, col, new_type, default_val in enum_conversions:
        try:
            db.session.execute(text(
                f"ALTER TABLE {table} ALTER COLUMN {col} TYPE {new_type} USING {col}::TEXT"
            ))
            db.session.execute(text(
                f"ALTER TABLE {table} ALTER COLUMN {col} SET DEFAULT {default_val}"
            ))
            db.session.commit()
            print(f"    {table}.{col} → {new_type}  OK")
        except Exception as e:
            db.session.rollback()
            print(f"    {table}.{col}: {e}")

    # ── 3. Add missing columns to 'orders' ────────────────────
    print("\n[3] Adding missing columns to 'orders'...")
    orders_cols = [
        ("delivery_fee",   "NUMERIC(10,2) DEFAULT 0"),
        ("platform_fee",   "NUMERIC(10,2) DEFAULT 0"),
        ("full_name",      "VARCHAR(200)"),
        ("phone",          "VARCHAR(20)"),
        ("address_line1",  "VARCHAR(300)"),
        ("address_line2",  "VARCHAR(300)"),
        ("city",           "VARCHAR(100)"),
        ("state",          "VARCHAR(100)"),
        ("pincode",        "VARCHAR(10)"),
        ("payment_method", "VARCHAR(50)"),
        ("payment_status", "VARCHAR(20) DEFAULT 'pending'"),
        ("status",         "VARCHAR(20) DEFAULT 'pending'"),
    ]
    for col, type_info in orders_cols:
        try:
            db.session.execute(text(
                f"ALTER TABLE orders ADD COLUMN IF NOT EXISTS {col} {type_info}"
            ))
            db.session.commit()
            print(f"    orders.{col}  OK")
        except Exception as e:
            db.session.rollback()
            print(f"    orders.{col}: {e}")

    # ── 4. Add missing columns to 'order_items' ───────────────
    print("\n[4] Adding missing columns to 'order_items'...")
    items_cols = [
        ("product_id", "INTEGER"),
        ("scrap_id",   "INTEGER"),
        ("seller_id",  "INTEGER"),
        ("title",      "VARCHAR(200) DEFAULT 'Unknown Item'"),
        ("price",      "NUMERIC(10,2) DEFAULT 0"),
        ("quantity",   "NUMERIC(10,2) DEFAULT 1"),
        ("unit",       "VARCHAR(20) DEFAULT 'unit'"),
    ]
    for col, type_info in items_cols:
        try:
            db.session.execute(text(
                f"ALTER TABLE order_items ADD COLUMN IF NOT EXISTS {col} {type_info}"
            ))
            db.session.commit()
            print(f"    order_items.{col}  OK")
        except Exception as e:
            db.session.rollback()
            print(f"    order_items.{col}: {e}")

    try:
        db.session.execute(text("ALTER TABLE order_items ALTER COLUMN product_id DROP NOT NULL"))
        db.session.execute(text("ALTER TABLE order_items ALTER COLUMN scrap_id DROP NOT NULL"))
        db.session.execute(text("ALTER TABLE order_items ALTER COLUMN unit_price DROP NOT NULL"))
        db.session.execute(text("ALTER TABLE order_items ALTER COLUMN total_price DROP NOT NULL"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"    order_items NOT NULL drop error: {e}")

    print("\n" + "=" * 60)
    print("  DB Sync Complete!")
    print("=" * 60)
