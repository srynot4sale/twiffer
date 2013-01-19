#!/usr/bin/python

import sqlite3
import outputty

def main():

    print 'Load database...'
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # Get ratings
    c.execute("SELECT user, COUNT(tweetid) FROM ratings GROUP BY user ORDER BY user")
    totals = c.fetchall()

    c.execute("SELECT user, COUNT(tweetid) FROM ratings WHERE rating = 2 GROUP BY user ORDER BY user")
    good = c.fetchall()

    c.execute("SELECT user, COUNT(tweetid) FROM ratings WHERE rating = 0 GROUP BY user ORDER BY user")
    bad = c.fetchall()

    utotals = {}
    ugood = {}
    ubad = {}

    for record in totals:
        utotals[record[0]] = record[1]

    for record in good:
        ugood[record[0]] = record[1]

    for record in bad:
        ubad[record[0]] = record[1]

    table = outputty.Table(headers=['Handle', 'Total', 'Good', 'Bad', 'Profile'])

    for user in utotals:
        total = float(utotals[user])

        if user in ugood:
            g = float(ugood[user])
        else:
            g = 0.0

        if user in ubad:
            b = float(ubad[user])
        else:
            b = 0.0

        table.append((user, int(total), '%d%%' % int((g/total) * 100), '%d%%' % int((b/total) * 100), 'http://twitter.com/%s' % user))

    table.order_by('Total', 'descending')
    print table

main()
