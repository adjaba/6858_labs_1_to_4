#!/usr/bin/python

import rpclib
import sys
import os
import sandboxlib
import urllib
import hashlib
import socket
import bank
import zoodb

import auth
# from zoodb import *

from debug import *

## Cache packages that the sandboxed code might want to import
import time
import errno

class ProfileAPIServer(rpclib.RpcServer):
    def __init__(self, user, visitor):
        self.user = user
        self.visitor = visitor
        db = zoodb.credential_setup()
        person = db.query(zoodb.Cred).get(self.user)
        self.token = person.token
        os.setgid(91011)
        os.setuid(91011)

    def rpc_get_self(self):
        return self.user

    def rpc_get_visitor(self):
        return self.visitor

    def rpc_get_xfers(self, username):
        xfers = []
        for xfer in bank.get_log(username):
            xfers.append({ 'sender': xfer.sender,
                           'recipient': xfer.recipient,
                           'amount': xfer.amount,
                           'time': xfer.time,
                         })
        return xfers

    def rpc_get_user_info(self, username):
        person_db = zoodb.person_setup()
        p = person_db.query(zoodb.Person).get(username)
        if not p:
            return None
        return { 'username': p.username,
                 'profile': p.profile,
                 'zoobars': bank.balance(username),
               }

    def rpc_xfer(self, target, zoobars):
        # with rpclib.client_connect('/authsvc/sock') as c:
        #     token = c.call('get_token', username=self.user)
        bank.transfer(self.user, target, zoobars, self.token)

def run_profile(pcode, profile_api_client):
    globals = {'api': profile_api_client}
    exec pcode in globals

class ProfileServer(rpclib.RpcServer):
    def rpc_run(self, pcode, user, visitor):
        uid = 91010 # uid from zook.conf

        import base64
        file_name_string = base64.urlsafe_b64encode(user)
        userdir = '/tmp/' + file_name_string#''.join(x for x in user if x.isalnum())
        if not os.path.exists(userdir):
            os.mkdir(userdir)
            os.chown(userdir, 91010, 55)
        if not os.path.exists(userdir):
            print 'Did not make userdir: ' + userdir
        (sa, sb) = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        pid = os.fork()
        if pid == 0:
            if os.fork() <= 0:
                sa.close()
                ProfileAPIServer(user, visitor).run_sock(sb)
                sys.exit(0)
            else:
                sys.exit(0)
        sb.close()
        os.waitpid(pid, 0)

        sandbox = sandboxlib.Sandbox(userdir, uid, '/profilesvc/lockfile')
        with rpclib.RpcClient(sa) as profile_api_client:
            return sandbox.run(lambda: run_profile(pcode, profile_api_client))

(_, dummy_zookld_fd, sockpath) = sys.argv

s = ProfileServer()
s.run_sockpath_fork(sockpath)
