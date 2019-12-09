from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models, utils


if os.path.exists("app.db"):
    #init the admin user
    u = models.User.query.filter_by(username='admin').first()
    if(u!=None):
        u.mfaid=Config.SPELLCHECK_ADMIN_MFA
        u.setpw(Config.SPELLCHECK_ADMIN_PW)
        db.session.commit()
else:
    db.create_all()
    u = models.User(username='admin', level=0, mfaid=Config.SPELLCHECK_ADMIN_MFA)
    u.setpw(Config.SPELLCHECK_ADMIN_PW)
    db.session.add(u)
    db.session.commit()
        