from zoodb import *
from debug import *

import hashlib
import random

def newtoken(cred_db, cred):
    hashinput = "%s%.10f" % (cred.password, random.random())
    cred.token = hashlib.md5(hashinput).hexdigest()
    cred_db.commit()
    return cred.token

def login(username, password):
    cred_db = credential_setup()
    cred = cred_db.query(Cred).get(username)
    if not cred:
        return None
    if cred.password == password:
        return newtoken(cred_db, cred)
    else:
        return None

def register(username, password):
    db = person_setup()
    person = db.query(Person).get(username)
    if person:
        return None
    newperson = Person()
    newperson.username = username
    # newperson.password = password
    db.add(newperson)
    db.commit()
    
    cred_db = credential_setup()
    cred = cred_db.query(Cred).get(username)
    if cred:
        return None
    newcred = Cred()
    newcred.username = username
    newcred.password = password
    cred_db.add(newcred)
    cred_db.commit()
    return newtoken(cred_db, newcred)

def check_token(username, token):
    db = credential_setup()
    person = db.query(Cred).get(username)
    if person and person.token == token:
        return True
    else:
        return False

