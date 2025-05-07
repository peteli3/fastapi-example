from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import DB

class Authentication:
    def __init__(self, db: 'DB'):
        self.db = db

    def verify_credentials(self, email, password):
        with self.db.Connection() as curs:
            curs.execute("""SELECT (password_hash = crypt(%(password)s, password_hash)) AS verified
                            FROM users
                            WHERE email = %(email)s;""",
                            { 'email': email,
                              'password': password.decode() })
            row = curs.fetchone()
            return bool(row[0])