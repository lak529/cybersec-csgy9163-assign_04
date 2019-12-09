import os
basedir = os.path.abspath(os.path.dirname(__file__))

def readfile(file):
    ret = None
    f = None
    try:
        with open(file, "r") as f:
            ret = f.read()
    except:
        ret = None
    return ret

class Config(object):
    # used by flask to init crypto, flask-wtf uses to protect against CSRF
    SECRET_KEY = os.environ.get('/run/secrets/spell_check_secret_key') or 'guess'
    
    #setup sqlalchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    #DB_USER = os.environ.get('DB_USER') or 'testuser'
    #DB_PASS = os.environ.get('DB_PASS') or '123'
    #DB_PROJ = os.environ.get('DB_PROJ') or 'assign_3'
    #SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + DB_USER + ':' + DB_PASS + '@localhost:3306/' + DB_PROJ
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #setup app tools
    SPELLCHECK_TEMP_DIR = os.environ.get('SPELLCHECK_TEMPDIR') or os.path.join(basedir, 'temp')
    SPELLCHECK_BIN_DIR = os.environ.get('SPELLCHECK_BINDIR') or os.path.join(basedir, 'bin')
    SPELLCHECK_TOOL = os.environ.get('SPELLCHECK_TOOL') or os.path.join(SPELLCHECK_BIN_DIR, 'spell_check')
    SPELLCHECK_WORDLIST = os.environ.get('SPELLCHECK_WORDLIST') or os.path.join(SPELLCHECK_BIN_DIR, 'wordlist.txt')
    
    SPELLCHECK_ADMIN_PW = readfile('/run/secrets/spell_check_admin_pw') or 'Administrator@1'
    SPELLCHECK_ADMIN_MFA = readfile('/run/secrets/spell_check_admin_mfa') or '12345678901'



