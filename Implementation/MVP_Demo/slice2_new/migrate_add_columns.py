from sqlalchemy import create_engine, inspect, text
from app.models import Base  # ← 改成你的实际路径

engine = create_engine("sqlite:///./app.db")  # ← 改成你的实际db路径
insp = inspect(engine)
for table in Base.metadata.tables.values():
    existing = {c["name"] for c in insp.get_columns(table.name)}
    for col in table.columns:
        if col.name not in existing:
            ddl = f"ALTER TABLE {table.name} ADD COLUMN {col.name} {col.type.compile(dialect=engine.dialect)}"
            with engine.begin() as conn:
                conn.execute(text(ddl))
            print("added:", table.name, col.name)
