from app import db
from app.models import User
from config import Config
import os

def init_db():
    if os.path.exists("app.db"):
        return
    db.create_all()

    u = User(username='admin', level=0, mfaid=Config.SPELLCHECK_ADMIN_MFA)
    u.setpw(Config.SPELLCHECK_ADMIN_PW)
    db.session.add(u)
    db.session.commit()

