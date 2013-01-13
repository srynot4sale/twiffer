import sys, tty, termios, os
import sqlite3


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

    for user in utotals:
        print '%s %s' % (user, utotals[user])

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

        print '%s      %sgood     %sbad' % (user, round((g/total) * 100, 2), round((b/total) * 100, 2))


main()
