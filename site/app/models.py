from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
from flask_login import UserMixin
from app import db
from app import login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    mfaid = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    password_salt = db.Column(db.String(8))
    level = db.Column(db.Integer, default=1)
    logins = db.relationship('SecLog', backref='user', lazy='dynamic')
    tests = db.relationship('TestLog', backref='user', lazy='dynamic')
    
    def setpw(self, pw):
        salt = ''.join(secrets.choice(string.ascii_letters+string.digits) for i in range(8))
        self.password_hash = generate_password_hash(salt+pw)
        self.password_salt = salt
    
    def checkpw(self, pw):
        return check_password_hash(self.password_hash, self.password_salt+pw)
    
    def checkmfaid(self, mid):
        #print(self.mfaid+":"+mid)
        return (self.mfaid==mid)
    
    def testcount(self):
        ret = 0
        for tst in self.tests:
            ret = ret + 1
        return ret
    
    # self.ToString()
    def __repr__(self):
        return '<User {}>'.format(self.username)

#log a history of tests by users
class TestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime(), default=datetime.now)
    test_input = db.Column(db.Text())
    test_output = db.Column(db.Text())
    
    def comma_results(self):
        #reformat as comma sep
        arr = self.test_output.split("\n")
        ret = ', '.join(arr)
        return ret
        

#log user login/out
class SecLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    login_time = db.Column(db.DateTime(), default=datetime.now)
    logout_time = db.Column(db.DateTime(), default=datetime.min)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))



#note: all of these user utils should be switched to the user object
def query_tests(user):
    u = User.query.filter_by(username=user).first()
    if(u != None):
        return u.tests
    else:
        return None

def query_test(user, test_id):
    u = User.query.filter_by(username=user).first()
    if(u != None):
        t = u.tests.filter_by(id=test_id).first()
        if(t != None):
            return t
        else:
            return None
    else:
        return None
    
def query_logins(user):
    u = User.query.filter_by(username=user).first()
    if(u != None):
        return u.logins
    else:
        return None
    

def write_login(user):
    u = user #User.query.filter_by(username=user).first()
    if(u != None):
        login = SecLog(user=u)
        db.session.add(login)
        db.session.commit()
    else:
        print("ERR: login user not specified")
        
        
def write_logout(user):
    u = user #User.query.filter_by(username=user).first()
    if(u != None):
        login = u.logins.filter_by(logout_time=datetime.min).first()
        if(login != None):
            login.logout_time = datetime.now()
            db.session.commit()
        else:
            print("ERR: login not found on logout")
    else:
        print("ERR: logout user not specified")

def write_test(user, testin, testout):
    u = user #User.query.filter_by(username=user.username).first()
    if(u != None):
        tout_str = '\n'.join(testout)
        test = TestLog(user=u,test_input=testin,test_output=tout_str)
        db.session.add(test)
        db.session.commit()
    




