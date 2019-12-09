import os
import subprocess
import random
from datetime import datetime

from app import app
from config import Config

def perform_spellcheck(text, misspelled):
    filename = gen_tmpfn()
    if(not write_tmpfile(filename, text)):
        misspelled.append("Failed to write tmpfile")
        return -1
    outstr = ""
    (ec,outstr) = exec_check(filename)
    if(ec<0):
        misspelled.append("Failed to run spellcheck")
        misspelled.apped(outstr)
        cleanup_tmpfile(filename)
        return -2
    if(len(outstr)>100000):
        misspelled.append("misspelled results too long, greater then 100k")
        cleanup_tmpfile(filename)
        return -3
    #print(outstr)
    arr = outstr.split("\n")
    #print(arr)
    for m in arr:
        misspelled.append(m)
    #print(misspelled)
    
    cleanup_tmpfile(filename)
    return len(m)

def gen_tmpfn():
    dstr = datetime.now().strftime("%Y%m%d%H%M%S")
    rstr = str(random.randrange(0,1000000))
    ret = os.path.join(Config.SPELLCHECK_TEMP_DIR, dstr+rstr)
    return ret

def write_tmpfile(filename, text):
    ret = 0
    try:
        with open(filename, "w") as f:
            f.write(text)
        ret = 1
    except:
        ret = -1
    return ret

def exec_check(filename):
    ret = 0
    outstr = ""
    args = [Config.SPELLCHECK_TOOL, filename, Config.SPELLCHECK_WORDLIST]
    cmd = "'" + args[0] + "' '" + args[1] + "' '" + args[2] + "'"
    #print(args)
    #print(cmd)
    try:
        outstr = os.popen(cmd).read()
        #p = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        #(out,err) = p.communicate()
        #outstr = out.decode('ascii')
        #print(outstr)
        outstr = outstr.strip()
        #print(outstr)
        ret = 1
    except Exception as ex:
        ret = -1
        outstr = "Failed to perform spellcheck: " + str(ex)
        #print(outstr)
    return (ret,outstr)

def cleanup_tmpfile(filename):
    ret = 1
    try:
        os.remove(filename)
    except:
        ret = 0
    return ret

def check_password_complex(password):
    isascii = lambda s: (len(s) == len(s.encode()))
    s = password
    #ascii only, Ul#@
    if(isascii(s)):
        if(any(x.isupper() for x in s) and
           any(x.islower() for x in s) and 
           any(x.isdigit() for x in s) and
           any(x in s for x in r"~!@#$%^&*()_+-=<>?,./;:[]\{}|")):
            return True
    #unicode, skip the upper/lower requiremnt, but require alpha
    else:
        if(any(x.isalpha() for x in s) and 
           any(x.isdigit() for x in s) and
           any(x in s for x in r"~!@#$%^&*()_+-=<>?,./;:[]\{}|")):
            return True
    #doesn't meet requirements
    return False


