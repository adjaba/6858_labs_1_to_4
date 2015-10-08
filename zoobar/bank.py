from zoodb import *
from debug import *
import rpclib

import time

def transfer(sender, recipient, zoobars):
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('transfer', sender=sender, recipient=recipient, zoobars=zoobars)

def balance(username):
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('balance', username=username)

def get_log(username):
    # with rpclib.client_connect('/banksvc/sock') as c:
    #     return c.call('get_log', username=username)
    db = transfer_setup()
    return db.query(Transfer).filter(or_(Transfer.sender==username,
                                         Transfer.recipient==username))

def register(username):
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('register', username=username)
