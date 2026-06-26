import os
from contextlib import contextmanager

from dotenv import load_dotenv


load_dotenv()


class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "").strip()
        self.username = os.getenv("NEO4J_USERNAME", "").strip()
        self.password = os.getenv("NEO4J_PASSWORD", "").strip()
        self.database = os.getenv("NEO4J_DATABASE", "neo4j").strip() or "neo4j"
        self._driver = None

    @property
    def configured(self) -> bool:
        return bool(self.uri and self.username and self.password)

    def driver(self):
        if not self.configured:
            raise RuntimeError("Neo4j is not configured. Set NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD.")

        if self._driver is None:
            try:
                from neo4j import GraphDatabase
            except ImportError as exc:
                raise RuntimeError("neo4j Python package is not installed.") from exc

            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
            )

        return self._driver

    @contextmanager
    def session(self):
        driver = self.driver()
        session = driver.session(database=self.database)

        try:
            yield session
        finally:
            session.close()

    def verify(self) -> dict:
        if not self.configured:
            return {
                "configured": False,
                "available": False,
                "status": "not_configured",
                "message": "Neo4j environment variables are missing.",
            }

        try:
            driver = self.driver()
            driver.verify_connectivity()

            return {
                "configured": True,
                "available": True,
                "status": "connected",
                "uri": self.uri,
                "database": self.database,
            }
        except Exception as exc:
            return {
                "configured": True,
                "available": False,
                "status": "connection_failed",
                "uri": self.uri,
                "database": self.database,
                "error": str(exc),
            }

    def write(self, query: str, parameters: dict | None = None) -> list[dict]:
        parameters = parameters or {}

        with self.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def read(self, query: str, parameters: dict | None = None) -> list[dict]:
        parameters = parameters or {}

        with self.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def close(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None


neo4j_client = Neo4jClient()