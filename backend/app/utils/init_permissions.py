from sqlalchemy.orm import Session
from app.models.permission import Permission

PERMISSIONS = [
    {"name": "manage_students", "description": "Create, edit, and delete students"},
    {"name": "view_students", "description": "View student information"},
    {"name": "manage_groups", "description": "Create, edit, and delete groups"},
    {"name": "view_groups", "description": "View group information"},
    {"name": "manage_contracts", "description": "Create, edit, and delete contracts"},
    {"name": "view_contracts", "description": "View contract information"},
    {"name": "manage_payments", "description": "Create and manage payments"},
    {"name": "view_payments", "description": "View payment information"},
    {"name": "manage_attendance", "description": "Mark and manage attendance"},
    {"name": "view_attendance", "description": "View attendance records"},
    {"name": "view_reports", "description": "View system reports and statistics"},
    {"name": "manage_turnstile", "description": "Manage turnstile logs"},
    {"name": "view_turnstile", "description": "View turnstile logs"},
]


def init_permissions(db: Session):
    """Initialize default permissions in the database"""
    for perm_data in PERMISSIONS:
        existing_permission = db.query(Permission).filter(
            Permission.name == perm_data["name"]
        ).first()

        if not existing_permission:
            permission = Permission(**perm_data)
            db.add(permission)

    db.commit()
    print("Permissions initialized successfully!")
