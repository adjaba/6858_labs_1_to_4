#!/usr/bin/python
#
# Insert bank server code here.
#

from zoodb import *
import rpclib
import sys
from debug import *
import auth_client as auth

import time

class BankRpcServer(rpclib.RpcServer):
    def rpc_transfer(self, sender, recipient, zoobars, token):
        if not auth.check_token(sender, token):
            print 'in bank-server.py:17', sender, token
            raise ValueError()

        bank_db = bank_setup()
        senderp = bank_db.query(Bank).get(sender)
        recipientp = bank_db.query(Bank).get(recipient)

        sender_balance = senderp.zoobars - zoobars
        recipient_balance = recipientp.zoobars + zoobars

        if sender_balance < 0 or recipient_balance < 0:
            raise ValueError()

        senderp.zoobars = sender_balance
        recipientp.zoobars = recipient_balance
        bank_db.commit()

        transfer = Transfer()
        transfer.sender = sender
        transfer.recipient = recipient
        transfer.amount = zoobars
        transfer.time = time.asctime()

        transferdb = transfer_setup()
        transferdb.add(transfer)
        transferdb.commit()

    def rpc_balance(self, username):
        db = bank_setup()
        bank = db.query(Bank).get(username)
        return bank.zoobars

    # def rpc_get_log(self, username):
    #     db = transfer_setup()
    #     objects = db.query(Transfer).filter(or_(Transfer.sender==username,
    #                                          Transfer.recipient==username))
    #     # return map(lambda x: x.__dict__, objects)
    #     return map(vars, objects)

    def rpc_register(self, username):
        bank_db = bank_setup()
        bank = bank_db.query(Bank).get(username)
        if bank:
            return None
        newbank = Bank()
        newbank.username = username
        newbank.zoobars = 10
        bank_db.add(newbank)
        bank_db.commit()

(_, dummy_zookld_fd, sockpath) = sys.argv

s = BankRpcServer()
s.run_sockpath_fork(sockpath)
