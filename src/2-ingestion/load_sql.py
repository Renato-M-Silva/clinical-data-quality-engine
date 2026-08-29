import os
import pandas as pd
from sqlalchemy import create_engine, text

class SQLIngestion:
    """
    SQL ingestion module for the DQIE pipeline.
    Loads SQL dump files (CREATE TABLE + INSERT INTO) from the Bronze Layer
    into in-memory SQLite tables, returning Pandas DataFrames.
    """

    def __init__(self, sql_base_path="data/1-bronze/sql"):
        self.sql_base_path = sql_base_path

        # In-memory SQLite database
        self.engine = create_engine("sqlite:///:memory:")

    def _full_path(self, filename):
        """Build full path for SQL file inside the Bronze Layer."""
        return os.path.join(self.sql_base_path, filename)

    def load(self, filename):
        """
        Load a .sql file into SQLite and return a DataFrame.
        Steps:
        - Validate file existence
        - Execute SQL script (CREATE TABLE + INSERT INTO)
        - Detect table name automatically
        - Return DataFrame
        """
        full_path = self._full_path(filename)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"SQL file not found: {full_path}")

        # Read SQL script
        with open(full_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Execute SQL script
        with self.engine.connect() as conn:
            conn.execute(text(sql_script))

        # Infer table name from filename
        table_name = filename.replace(".sql", "")

        # Load into DataFrame
        df = pd.read_sql(f"SELECT * FROM {table_name}", self.engine)

        print(f"Loaded SQL table: {table_name}  |  Shape: {df.shape}")
        return df


if __name__ == "__main__":
    ingestion = SQLIngestion()

    patients_df = ingestion.load("patients.sql")
    sessions_df = ingestion.load("sessions.sql")

    print("\nPreview:")
    print(patients_df.head())
