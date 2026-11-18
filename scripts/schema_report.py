"""Read-only preview of DB vs declared SQLAlchemy metadata; NEVER runs DDL."""
from sqlalchemy import inspect
from app.db import Base, engine
import app.models  # noqa: F401


def report():
    inspector = inspect(engine)
    existing = set(inspector.get_table_names()) - {"alembic_version"}
    target = set(Base.metadata.tables)
    print("Jadval soni, DB/Model:", len(existing), "/", len(target))
    for label, names in (("MISSING TABLES", target - existing), ("EXTRA TABLES", existing - target)):
        print(label, sorted(names))
    for name in sorted(existing & target):
        actual_cols = {c["name"]: c for c in inspector.get_columns(name)}
        target_cols = {c.name: c for c in Base.metadata.tables[name].columns}
        missing = target_cols.keys() - actual_cols.keys()
        extra = actual_cols.keys() - target_cols.keys()
        if missing or extra:
            print(f"{name}: missing columns={sorted(missing)}, extra columns={sorted(extra)}")
        for col_name in sorted(actual_cols.keys() & target_cols.keys()):
            actual, wanted = actual_cols[col_name], target_cols[col_name]
            if actual["nullable"] != wanted.nullable:
                print(f"{name}.{col_name}: nullability DB={actual['nullable']}, MODEL={wanted.nullable}")
            if actual["type"].__class__.__name__ != wanted.type.__class__.__name__:
                print(f"{name}.{col_name}: type DB={actual['type']}, MODEL={wanted.type}")
    print("WARNING: Read-only report is NOT full schema proof (FK/index/default parity needs manual review).")


if __name__ == "__main__":
    report()
