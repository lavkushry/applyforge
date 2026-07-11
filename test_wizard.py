from app.db.session import SessionLocal
from app.models.entities import User
db = SessionLocal()
user = db.query(User).first()
if user:
    print(user.id)
