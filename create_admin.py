"""
Create first admin user for Sisi Lola Control Center
Run this once after database initialization
"""
import sys
sys.path.insert(0, 'sisi_lola_api')

from app.database import SessionLocal, UserModel, RoleModel, init_db
from app.auth import get_password_hash

# Initialize database first
print("Initializing database...")
init_db()

db = SessionLocal()

# Check if admin already exists
existing = db.query(UserModel).filter(UserModel.email == "admin@sisilola.io").first()
if existing:
    print("Admin user already exists!")
    db.close()
    sys.exit(0)

# Create admin user
print("Creating admin user...")
admin = UserModel(
    email="admin@sisilola.io",
    password_hash=get_password_hash("SisiLola2025!")
)
db.add(admin)
db.commit()
db.refresh(admin)

# Assign SUPER_ADMIN role
role = db.query(RoleModel).filter(RoleModel.name == "SUPER_ADMIN").first()
if role:
    admin.roles.append(role)
    db.commit()
    print(f"✓ Admin user created: {admin.email}")
    print(f"✓ Password: SisiLola2025!")
    print(f"✓ Role: SUPER_ADMIN")
    print("\n⚠️  IMPORTANT: Change this password immediately after first login!")
else:
    print("ERROR: SUPER_ADMIN role not found")

db.close()
