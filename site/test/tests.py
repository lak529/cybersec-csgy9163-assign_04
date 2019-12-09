import unittest
import requests
from bs4 import BeautifulSoup
import os
import random
import string



debug = False

baseurl = "http://127.0.0.1:5000"
fake_user = "fake"
fake_pass = "fakepass1!"
fake_mfaid = "fake"

#japanese, but text files don't support utf-16
#   [watashi][wa][runa]@9@9
uc_str = text = '\u79c1\u306f\u30eb\u30ca\u0040\u0039\u0040\u0039'.encode().decode()

valid_user = "gooduser"
valid_pass = "Goodpass!1"
valid_mfaid = "goodmfaid"

check_text = "this ixxxi a sentxxx"
check_misspelled = ["ixxxi", "sentxxx"]

nonasc = [] 
for i in range(65536):
    nonasc.append(chr(i))

def GET_parse(session, url, elem, attr):
    r = session.get(url)
    resp = r.text
    page = BeautifulSoup(resp, "html.parser")
    obj = page.find(id=elem)
    res = ""
    if(obj!=None):
        if(attr!=None):
            res = obj[attr]
        else:
            res = ""
            for s in obj.strings:
                res += s
    return (res,resp)

def POST_parse(session, url, payload, elem, attr):
    r = session.post(url, data=payload)
    resp = r.text
    page = BeautifulSoup(resp, "html.parser")
    obj = page.find(id=elem)
    res = ""
    if(obj!=None):
        if(attr!=None):
            res = obj[attr]
        else:
            res = ""
            for s in obj.strings:
                res += s
    return (r,res,resp)

def send_login(session, uname, pword, mfaid):
    url = baseurl+"/login"
    (csrf_token,resp) = GET_parse(session, url, "csrf_token", "value")
    
    payload = {'username': uname, 'password': pword, 'mfacode': mfaid, 'csrf_token': csrf_token, 'submit': "Sign+In"}
    (r,res,resp) = POST_parse(session, url, payload, "result", None)
    if(debug):
        print(res)
    return (r,res,resp)

def send_register(session, uname, pword, mfaid):
    url = baseurl+"/register"    
    (csrf_token,resp) = GET_parse(session, url, "csrf_token", "value")
    
    payload = {'username': uname, 'password': pword, 'mfaid': mfaid, 'csrf_token': csrf_token, 'submit': "Register"}
    (r,res,resp) = POST_parse(session, url, payload, "success", None)
    if(debug):
        print(res)
    return (r,res,resp)

def send_spellcheck(session, text):
    url = baseurl+"/spell_check"    
    (csrf_token,resp) = GET_parse(session, url, "csrf_token", "value")
    
    #text=text.replace(' ', '+')
    payload = {'textin': text, 'csrf_token': csrf_token, 'submit': "Check+Text"}
    (r,res,resp) = POST_parse(session, url, payload, "misspelled", None)
    if(debug):
        print(res)
    #print(resp)
    return (r,res,resp)

def test_LoginBadUser():
    session = requests.Session()
    (r,res,resp) = send_login(session, fake_user, fake_pass, fake_mfaid)
    return ("Incorrect" in res)
    
def test_LoginBadMFAid():
    session = requests.Session()
    (r,res,resp) = send_login(session, valid_user, valid_pass, fake_mfaid)
    return (("Two-factor" in res) and ("failure" in res))

def test_RegisterUser_Valid(uname,pword,mfaid):
    session = requests.Session()
    (r,res,resp) = send_register(session, uname, pword, mfaid)
    return ("success" in res)

def test_RegisterUser_BadPass():
    session = requests.Session()
    (r,res,resp) = send_register(session, fake_user, fake_pass, fake_mfaid)
    return ("failure" in res)

def test_LoginGoodUser(uname,pword,mfaid):
    session = requests.Session()
    (r,res,resp) = send_login(session, uname, pword, mfaid)
    return ("success" in res)
    
def test_CSRF_Login():
    session = requests.Session()
    #no csrf token!
    payload = {'username': valid_user, 'password': valid_pass, 'mfacode': valid_mfaid, 'submit': "Sign+In"}
    (r,res,resp) = POST_parse(session, baseurl+"/login", payload, "result", None)
    #we should be directed to login
    return ("Sign In" in resp)


def match_misspelled(check_msp, msp):
    if(debug):
        print(str(check_msp)+":"+str(msp))
    for s in check_msp:
        if(s not in msp):
            return False
    return True
    
def test_MalignSpellCheck(test):
    session = requests.Session()
    (r,res,resp) = send_login(session, valid_user, valid_pass, valid_mfaid)
    
    if(test==1):    #large
        msp = ["textt"]
        #text = ''.join(random.choice(string.printable) for i in range(2000000))
        text = 'x ' * 1000000
        text += " "+msp[0]
        (r,res,resp) = send_spellcheck(session, text)
    elif(test==2):   #non-ascii
        msp = ["textt"]
        text = uc_str
        text += " "+msp[0]
        (r,res,resp) = send_spellcheck(session, text)
    elif(test==3):    #rand print large
        msp = []    #this crashes the spellcheck, so no resutls
        text = ''.join(random.choice(string.printable) for i in range(30000))
        text += " textt"
        (r,res,resp) = send_spellcheck(session, text)
    elif(test==4):    #rand print small
        msp = ["textt"]
        text = ''.join(random.choice(string.printable) for i in range(10000))
        text += " "+msp[0]
        (r,res,resp) = send_spellcheck(session, text)
    return match_misspelled(msp,res)

def test_SpellCheck(text,msp):
    session = requests.Session()
    (r,res,resp) = send_login(session, valid_user, valid_pass, valid_mfaid)
    (r,res,resp) = send_spellcheck(session, text)
    return match_misspelled(msp,res)

def test_SessionManagement():
    session = requests.Session()
    #not logged in, shoudln't allow
    (r,res,resp) = send_spellcheck(session, check_text)
    return ("Misspelled Words" not in resp)
    
def test_UC_SC():
    text = uc_str
    msp = []
    session = requests.Session()
    (r,res,resp) = send_login(session, uc_str, valid_pass, valid_mfaid)
    (r,res,resp) = send_spellcheck(session, text)
    return match_misspelled(msp,res)
    

def init_tests():
    payload = {'mkey': 'eightfoldwitch'}
    r = requests.post(baseurl+"/api/tests/resetall", data=payload)

def run_basetests():
    print("init:                "+str(init_tests()))
    print("login bad user:      "+str(test_LoginBadUser()))
    print("register user:       "+str(test_RegisterUser_Valid()))
    print("login bad mfaid:     "+str(test_LoginBadMFAid()))
    print("login good user:     "+str(test_LoginGoodUser(valid_user,valid_pass,valid_mfaid)))
    print("spellcheck:          "+str(test_SpellCheck(check_text,check_misspelled)))




class TestNormalUsage(unittest.TestCase):
    def test_LoginGood(self):
        init_tests()
        test_RegisterUser_Valid(valid_user,valid_pass,valid_mfaid)
        self.assertTrue(test_LoginGoodUser(valid_user,valid_pass,valid_mfaid))
        
    def test_CSRF(self):
        init_tests()
        test_RegisterUser_Valid(valid_user,valid_pass,valid_mfaid)
        self.assertTrue(test_CSRF_Login())
        
    def test_LoginBad(self):
        init_tests()
        self.assertTrue(test_LoginBadUser())
        
    def test_RegisterDup(self):
        init_tests()
        test_RegisterUser_Valid(valid_user,valid_pass,valid_mfaid)
        self.assertFalse(test_RegisterUser_Valid(valid_user,valid_pass,valid_mfaid)) #dup register should fail
        
    def test_RegisterGood(self):
        init_tests()
        self.assertTrue(test_RegisterUser_Valid(valid_user,valid_pass,valid_mfaid))
        
    def test_SpellCheck(self):
        init_tests()
        test_RegisterUser_Valid(valid_user,valid_pass,valid_mfaid)
        self.assertTrue(test_SpellCheck(check_text,check_misspelled))
    
    def test_UnicodeStrs(self):
        init_tests()
        self.assertTrue(test_RegisterUser_Valid(uc_str,valid_pass,valid_mfaid))
        self.assertTrue(test_LoginGoodUser(uc_str,valid_pass,valid_mfaid))
        text = uc_str
        msp = []
        session = requests.Session()
        (r,res,resp) = send_login(session, uc_str, valid_pass, valid_mfaid)
        (r,res,resp) = send_spellcheck(session, text)
        self.assertTrue(match_misspelled(msp,res))
    
    def test_SessionManagement(self):
        init_tests()
        test_RegisterUser_Valid(valid_user,valid_pass,valid_mfaid)
        self.assertTrue(test_SessionManagement()) #not logged in, shouldn't allow
        self.assertTrue(test_LoginGoodUser(valid_user,valid_pass,valid_mfaid))
        self.assertTrue(test_SessionManagement()) #even after another session login, it still shouldn't be allowed


class TestBadUsage(unittest.TestCase):
    def test_MalignSpellCheck(self):
        init_tests()
        test_RegisterUser_Valid(valid_user,valid_pass,valid_mfaid)
        self.assertTrue(test_MalignSpellCheck(1))
        self.assertTrue(test_MalignSpellCheck(2))
        self.assertTrue(test_MalignSpellCheck(3))
        self.assertTrue(test_MalignSpellCheck(4))

    def test_MalignRegister(self):
        init_tests()
        malign_user = ''.join(random.choice(string.printable) for i in range(30000))
        malign_pass = malign_user
        self.assertTrue(test_RegisterUser_Valid(malign_user,malign_pass,valid_mfaid))
        self.assertTrue(test_LoginGoodUser(malign_user,malign_pass,valid_mfaid))

if(__name__=='__main__'):
    unittest.main()

