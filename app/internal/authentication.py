from fastapi import Request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import DB

def require_auth(request: Request):
    return request.state.user_email if request.state.authenticated else None

class Authentication:
    def __init__(self, db: 'DB'):
        self.db = db

    def verify_credentials(self, email, password):
        with self.db.Connection() as curs:
            curs.execute("""SELECT id, (password_hash = crypt(%(password)s, password_hash)) AS verified
                            FROM users
                            WHERE email = %(email)s;""",
                            { 'email': email,
                              'password': password.decode() })
            row = curs.fetchone()
            verified = row[1]
            return row if verified else None