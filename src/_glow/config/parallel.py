from pathlib import Path
import random
import sqlite3
import dill as pickle
import os
import threading
from typing import Optional, List, Tuple
from time import sleep

from _glow.device.dev import Dev


class ParallelServer:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.lock = threading.RLock()

    def __repr__(self):
        return f"<DevServer(db={self.db_path}, devices={len(self.list())})>"

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS devices (
                    dev_id TEXT PRIMARY KEY,
                    data BLOB NOT NULL,
                    is_occupied BOOLEAN NOT NULL DEFAULT 0,
                    created_at REAL DEFAULT (strftime('%s.%f', 'now')),
                    updated_at REAL DEFAULT (strftime('%s.%f', 'now'))
                )
            """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_occupied ON devices (is_occupied);"
            )

    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)

    def put(self, dev_id: str, dev: Dev):
        """insert or return a device to db.

        :param dev_id: dev unique id
        :dev: Dev object
        """
        data = pickle.dumps(dev)

        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE devices
                SET data = ?, is_occupied = 0, updated_at = strftime('%s.%f', 'now')
                WHERE dev_id = ?
            """,
                (data, dev_id),
            )

            if cursor.rowcount == 0:
                conn.execute(
                    """
                    INSERT INTO devices (dev_id, data, is_occupied, created_at, updated_at)
                    VALUES (?, ?, 0, strftime('%s.%f', 'now'), strftime('%s.%f', 'now'))
                """,
                    (dev_id, data),
                )

    def get(self) -> Optional[Tuple[str, Dev]]:
        """apply a dev from db.

        :return: None or (dev_id, Dev)
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT dev_id, data FROM devices WHERE is_occupied = 0"
            ).fetchall()

            if not rows:
                return None

            dev_id, data = random.choice(rows)

            conn.execute(
                """
                UPDATE devices
                SET is_occupied = 1, updated_at = strftime('%s.%f', 'now')
                WHERE dev_id = ?
            """,
                (dev_id,),
            )

            dev = pickle.loads(data)
            return (dev_id, dev)


class ParallelClient:
    def __init__(self, db_path: Path):
        self.pool = ParallelServer(db_path)

    def put(self, dev: Dev):
        self.pool.put(dev.id, dev)

    def get(self) -> Dev:
        dev: Dev = None
        while True:
            if not dev:
                _, dev = self.pool.get()
            else:
                return dev
            sleep(0.5)
