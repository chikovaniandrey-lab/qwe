from database import async_session

with async_session() as db:
    db.execute()