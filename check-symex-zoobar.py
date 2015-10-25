#!/usr/bin/env python2

verbose = True

import symex.fuzzy as fuzzy
import __builtin__
import inspect
import symex.importwrapper as importwrapper
import symex.rewriter as rewriter

importwrapper.rewrite_imports(rewriter.rewriter)

import symex.symflask
import symex.symsql
import symex.symeval
import zoobar

def startresp(status, headers):
  if verbose:
    print 'startresp', status, headers

def report_balance_mismatch():
  print "WARNING: Balance mismatch detected"

def report_zoobar_theft():
  print "WARNING: Zoobar theft detected"

def adduser(pdb, username, token):
  u = zoobar.zoodb.Person()
  u.username = username
  u.token = token
  pdb.add(u)

def test_stuff():
  pdb = zoobar.zoodb.person_setup()
  pdb.query(zoobar.zoodb.Person).delete()
  adduser(pdb, 'alice', 'atok')
  adduser(pdb, 'bob', 'btok')
  balance1 = sum([p.zoobars for p in pdb.query(zoobar.zoodb.Person).all()])
  all_balances_1 = {p.username: p.zoobars for p in pdb.query(zoobar.zoodb.Person).all()}
  people1 = sum([1 for p in pdb.query(zoobar.zoodb.Person).all()])
  pdb.commit()

  tdb = zoobar.zoodb.transfer_setup()
  tdb.query(zoobar.zoodb.Transfer).delete()
  tdb.commit()

  environ = {}
  environ['wsgi.url_scheme'] = 'http'
  environ['wsgi.input'] = 'xxx'
  environ['SERVER_NAME'] = 'zoobar'
  environ['SERVER_PORT'] = '80'
  environ['SCRIPT_NAME'] = 'script'
  environ['QUERY_STRING'] = 'query'
  environ['HTTP_REFERER'] = fuzzy.mk_str('referrer')
  environ['HTTP_COOKIE'] = fuzzy.mk_str('cookie')

  ## In two cases, we over-restrict the inputs in order to reduce the
  ## number of paths that "make check" explores, so that it finishes
  ## in a reasonable amount of time.  You could pass unconstrained
  ## concolic values for both REQUEST_METHOD and PATH_INFO, but then
  ## zoobar generates around 2000 distinct paths, and that takes many
  ## minutes to check.

  # environ['REQUEST_METHOD'] = fuzzy.mk_str('method')
  # environ['PATH_INFO'] = fuzzy.mk_str('path')
  environ['REQUEST_METHOD'] = 'GET'
  environ['PATH_INFO'] = 'trans' + fuzzy.mk_str('path')

  if environ['PATH_INFO'].startswith('//'):
    ## Don't bother trying to construct paths with lots of slashes;
    ## otherwise, the lstrip() code generates lots of paths..
    return

  resp = zoobar.app(environ, startresp)
  if verbose:
    for x in resp:
      print x

  ## Exercise 6: your code here.

  ## Detect balance mismatch.
  ## When detected, call report_balance_mismatch()
  balanceEnd = sum([p.zoobars for p in pdb.query(zoobar.zoodb.Person).all()])
  peopleEnd = sum([1 for p in pdb.query(zoobar.zoodb.Person).all()])
  if balance1 != balanceEnd and people1 == peopleEnd:
    report_balance_mismatch() # detects 8

  ## Detect zoobar theft.
  ## When detected, call report_zoobar_theft()
  all_balances_end = {p.username: p.zoobars for p in pdb.query(zoobar.zoodb.Person).all()}
  if (len(all_balances_1.keys()) == len(all_balances_end.keys()) and
      set(all_balances_1.keys()) == set(all_balances_end.keys())):
    # same number and set of users
    diff_balance_users = []
    for user in all_balances_1:
      if all_balances_1[user] != all_balances_end[user]:
        diff_balance_users.append(user)
        # check no txns exist

    '''check all the users with different balances that they have entries in the
    Transfer table.'''
    tdb = zoobar.zoodb.transfer_setup()
    for user in diff_balance_users:
      net_balance_change = 0
      user_transfers = tdb.query(zoobar.zoodb.Transfer).filter_by(sender=user)
      for transfer in user_transfers:
        net_balance_change -= transfer.amount
      user_transfers = tdb.query(zoobar.zoodb.Transfer).filter_by(recipient=user)
      for transfer in user_transfers:
        net_balance_change += transfer.amount
      if all_balances_end[user] != all_balances_1[user] + net_balance_change:
        report_zoobar_theft() # detects 8

fuzzy.concolic_test(test_stuff, maxiter=2000, verbose=1)

