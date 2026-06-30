import json
from database import db_manager

class User:
    """Handles User Authentication models using direct OOP paradigms."""
    def __init__(self, user_id: int, username: str):
        self.id = user_id
        self.username = username

    @classmethod
    def register(cls, username: str, password_hash: str) -> bool:
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)", 
                    (username, password_hash)
                )
            return True
        except RuntimeError:
            return False

    @classmethod
    def authenticate(cls, username: str, password_hash: str):
        with db_manager.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?", 
                (username, password_hash)
            )
            row = cursor.fetchone()
            if row:
                return cls(row['id'], row['username'])
        return None


class ResumeReport:
    """Handles data transactions for persistent Resume Reports."""
    def __init__(self, report_id: int, user_id: int, filename: str, timestamp: str, score: int, data_json: str):
        self.id = report_id
        self.user_id = user_id
        self.filename = filename
        self.timestamp = timestamp
        self.score = score
        self.data = json.loads(data_json)

    @classmethod
    def save(cls, user_id: int, filename: str, score: int, data_dict: dict) -> int:
        with db_manager.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO analysis_history (user_id, filename, score, parsed_json) VALUES (?, ?, ?, ?)",
                (user_id, filename, score, json.dumps(data_dict))
            )
            return cursor.lastrowid

    @classmethod
    def get_by_user(cls, user_id: int) -> list:
        reports = []
        with db_manager.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM analysis_history WHERE user_id = ? ORDER BY timestamp DESC", 
                (user_id,)
            )
            rows = cursor.fetchall()
            for r in rows:
                reports.append(cls(r['id'], r['user_id'], r['filename'], r['timestamp'], r['score'], r['parsed_json']))
        return reports

    @classmethod
    def get_by_id(cls, report_id: int, user_id: int):
        with db_manager.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM analysis_history WHERE id = ? AND user_id = ?", 
                (report_id, user_id)
            )
            r = cursor.fetchone()
            if r:
                return cls(r['id'], r['user_id'], r['filename'], r['timestamp'], r['score'], r['parsed_json'])
        return None