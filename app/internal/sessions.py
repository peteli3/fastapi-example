from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .db import DB

class SessionManager:
    def __init__(self, db: 'DB'):
        self.db = db
        self.sessions = {}

    def create_session(self, user_id, user_agent):
        token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=30)
        with self.db.Connection() as curs:
            curs.execute("""INSERT INTO sessions (token, user_id, expires_at, user_agent)
                            VALUES (%s, %s, %s, %s);""",
                        (token, user_id, expires_at, user_agent))
        return token

    def get_user_from_session(self, token):
        with self.db.Connection() as curs:
            curs.execute("""SELECT u.id, u.email
                            FROM users u
                            JOIN sessions s on u.id = s.user_id
                            WHERE s.token = %s AND s.expires_at > now();""",
                            (token, ))
            row = curs.fetchone()
            return row if row else None

    def delete_session(self, token):
        with self.db.Connection() as curs:
            curs.execute("""DELETE FROM sessions
                            WHERE token = %s
                            RETURNING token;""",
                        (token, ))
            deleted = curs.fetchone()
            return deleted is not None
