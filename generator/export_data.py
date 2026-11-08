
import csv
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import MetaData, select

from database.connection import engine
from database import models  # Ensure all ORM models are registered


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_DIR = PROJECT_ROOT / "data" / "csv"
JSON_DIR = PROJECT_ROOT / "data" / "json"
SQL_DIR = PROJECT_ROOT / "data" / "sql"


def json_serializer(value):
    """Convert database values into JSON-compatible values."""

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    return str(value)


def export_table_to_csv(connection, table):
    """Export one database table to CSV."""

    output_path = CSV_DIR / f"{table.name}.csv"

    result = connection.execute(select(table))
    rows = result.mappings().all()

    column_names = list(table.columns.keys())

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=column_names
        )

        writer.writeheader()

        for row in rows:
            writer.writerow({
                column: json_serializer(row[column])
                if row[column] is not None
                else ""
                for column in column_names
            })

    print(
        f"[CSV] {table.name}: {len(rows)} records"
    )


def export_table_to_json(connection, table):
    """Export one database table to JSON."""

    output_path = JSON_DIR / f"{table.name}.json"

    result = connection.execute(select(table))
    rows = result.mappings().all()

    records = [
        dict(row)
        for row in rows
    ]

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            default=json_serializer
        )

    print(
        f"[JSON] {table.name}: {len(records)} records"
    )


def export_sql_dump():
    """Export the complete SQLite database as a SQL script."""

    if engine.dialect.name != "sqlite":
        raise RuntimeError(
            "This SQL dump function currently supports SQLite only."
        )

    import sqlite3

    database_path = engine.url.database

    if not database_path:
        raise RuntimeError("SQLite database path could not be determined.")

    if database_path != ":memory:":
        database_path = str(Path(database_path).resolve())

    output_path = SQL_DIR / "yottaflex_database.sql"

    source_connection = sqlite3.connect(database_path)

    try:
        with output_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            for statement in source_connection.iterdump():
                file.write(statement + "\n")

    finally:
        source_connection.close()

    print("[SQL] Database dump:", output_path.name)


def main():
    print("\nYOTTAFLEX DATA EXPORT")
    print("=====================")

    CSV_DIR.mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    SQL_DIR.mkdir(parents=True, exist_ok=True)

    print("Database:", engine.url)
    print("Database type:", engine.dialect.name)

    metadata = MetaData()
    metadata.reflect(bind=engine)

    tables = sorted(
        metadata.sorted_tables,
        key=lambda table: table.name
    )

    if not tables:
        raise RuntimeError(
            "No database tables found. Check your database configuration."
        )

    print("Tables found:", len(tables))

    total_tables = 0

    with engine.connect() as connection:

        for table in tables:
            export_table_to_csv(connection, table)
            export_table_to_json(connection, table)
            total_tables += 1

    export_sql_dump()

    print("\n---------------------")
    print("EXPORT SUMMARY")
    print("---------------------")
    print("Tables exported:", total_tables)
    print("CSV directory:", CSV_DIR)
    print("JSON directory:", JSON_DIR)
    print("SQL directory:", SQL_DIR)
    print("\nDATA EXPORT: PASSED")


if __name__ == "__main__":
    main()
