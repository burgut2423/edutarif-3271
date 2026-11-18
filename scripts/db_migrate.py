"""Apply verified Alembic migrations, never silently stamp a legacy schema."""
from pathlib import Path
from alembic import command
from alembic.config import Config


def migrate_to_head():
    root = Path(__file__).resolve().parents[1]
    cfg = Config(str(root / "alembic.ini"))
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    migrate_to_head()
