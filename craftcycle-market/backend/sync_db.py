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

    # Manual column injection for existing 'orders' table
    from sqlalchemy import text
    cols = [
        ('delivery_fee', 'NUMERIC(10, 2) DEFAULT 0'),
        ('platform_fee', 'NUMERIC(10, 2) DEFAULT 0'),
        ('full_name', 'VARCHAR(200)'),
        ('phone', 'VARCHAR(20)'),
        ('address_line1', 'VARCHAR(300)'),
        ('address_line2', 'VARCHAR(300)'),
        ('city', 'VARCHAR(100)'),
        ('state', 'VARCHAR(100)'),
        ('pincode', 'VARCHAR(10)'),
        ('payment_method', 'VARCHAR(50)'),
        ('payment_status', 'VARCHAR(50) DEFAULT \'pending\'')
    ]
    
    print("Checking/Updating 'orders' table columns...")
    for col, type_info in cols:
        try:
            db.session.execute(text(f'ALTER TABLE orders ADD COLUMN IF NOT EXISTS {col} {type_info}'))
            db.session.commit()
            print(f"  - Column '{col}' checked/added.")
        except Exception as e:
            db.session.rollback()
            print(f"  - Error on column '{col}': {e}")
    
    print("\nDatabase sync complete!")
