from app import create_app
from extensions import db
import sys

app = create_app()
with app.app_context():
    print("Initializing database...")
    try:
        db.create_all()
        print("db.create_all() finished.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

    # If orders table exists but lacks columns, create_all won't help.
    # Let's manually check for delivery_fee column.
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('orders')]
    print(f"Current columns in 'orders': {columns}")

    if 'delivery_fee' not in columns:
        print("Adding 'delivery_fee' and 'platform_fee' to 'orders' table...")
        try:
            from sqlalchemy import text
            db.session.execute(text('ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_fee NUMERIC(10, 2) DEFAULT 0'))
            db.session.execute(text('ALTER TABLE orders ADD COLUMN IF NOT EXISTS platform_fee NUMERIC(10, 2) DEFAULT 0'))
            db.session.commit()
            print("Columns added successfully.")
        except Exception as e:
            print(f"Error adding columns: {e}")
            db.session.rollback()
