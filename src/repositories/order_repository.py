import sqlite3
from typing import List, Tuple, Optional
from .interfaces import IOrderRepository

class SQLiteOrderRepository(IOrderRepository):
    def __init__(self, db_path: str = 'loja.db') -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as db:
            c = db.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS ped 
                       ( id INTEGER PRIMARY KEY, cli TEXT, itens TEXT, 
                        tot REAL, st TEXT, dt TEXT, tp TEXT)''')
            db.commit()

    def insert(self, client: str, items_str: str, total: float, status: str, date: str, client_type: str) -> int:
        with sqlite3.connect(self.db_path) as db:
            c = db.cursor()
            c.execute(
                "INSERT INTO ped (cli, itens, tot, st, dt, tp) VALUES (?, ?, ?, ?, ?, ?)",
                (client, items_str, total, status, date, client_type)
            )
            db.commit()
            return int(c.lastrowid) if c.lastrowid else 0

    def get_by_id(self, order_id: int) -> Optional[Tuple]:
        with sqlite3.connect(self.db_path) as db:
            c = db.cursor()
            c.execute("SELECT * FROM ped WHERE id=?", (order_id,))
            return c.fetchone()

    def update_status(self, order_id: int, status: str) -> None:
        with sqlite3.connect(self.db_path) as db:
            c = db.cursor()
            c.execute("UPDATE ped SET st=? WHERE id=?", (status, order_id))
            db.commit()

    def get_all(self) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as db:
            c = db.cursor()
            c.execute("SELECT * FROM ped")
            return c.fetchall()

    def get_by_client(self, client: str) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as db:
            c = db.cursor()
            c.execute("SELECT * FROM ped WHERE cli=?", (client,))
            return c.fetchall()

    def get_distinct_clients(self) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as db:
            c = db.cursor()
            c.execute("SELECT DISTINCT cli, tp FROM ped")
            return c.fetchall()