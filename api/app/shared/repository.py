from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db_session: Session):
        self.db = db_session