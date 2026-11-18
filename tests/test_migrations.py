"""P0-01: fresh baseline / reversible schema / stable data / no silent legacy overwrite."""
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text, select
from app.db import Base
from app.models import District

ROOT = Path(__file__).resolve().parents[1]


def cfg_for(tmp_path):
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.attributes["database_url"] = f"sqlite:///{tmp_path / 'edutarif_migration.db'}"
    return cfg


def test_fresh_migration_roundtrip_and_data_survival(tmp_path):
    cfg = cfg_for(tmp_path)
    command.upgrade(cfg, "head")
    engine = create_engine(cfg.attributes["database_url"])
    assert set(Base.metadata.tables) <= set(inspect(engine).get_table_names())
    with engine.begin() as conn:
        conn.execute(District.__table__.insert().values(name="Sinov tumani"))
    command.upgrade(cfg, "head")  # idempotent with existing data
    with engine.connect() as conn:
        assert conn.scalar(select(District.name)) == "Sinov tumani"
    command.check(cfg)  # detected DB structure matches the declarative models
    command.downgrade(cfg, "base")  # destructive rollback ONLY on disposable test DB
    assert set(Base.metadata.tables).isdisjoint(inspect(engine).get_table_names())
    engine.dispose()


def test_legacy_database_is_not_silently_modified(tmp_path):
    cfg = cfg_for(tmp_path)
    engine = create_engine(cfg.attributes["database_url"])
    Base.metadata.create_all(engine)  # simulation of a pre-Alembic installation
    with engine.begin() as conn:
        conn.execute(District.__table__.insert().values(name="Eski tuman"))
    with pytest.raises(RuntimeError, match="Back up and verify"):
        command.upgrade(cfg, "head")
    with engine.connect() as conn:
        assert conn.scalar(select(District.name)) == "Eski tuman"
    engine.dispose()


def test_revision_and_initial_migration_exists():
    assert (ROOT / "migrations/versions/20261119_01_baseline_schema_20_tables.py").exists()
    assert len(Base.metadata.tables) == 20
