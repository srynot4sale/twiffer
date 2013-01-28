#!/usr/bin/python

import sqlite3
import os, sys, time, urllib2
import outputty, twitter
import config

def main():

    db_path = os.path.join(sys.path[0], 'data.db')

    print 'Load database...'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print 'Authenticating...'
    twitter_stream = twitter.Twitter(
            auth=config.auth,
            secure=1,
            api_version='1.1',
            domain='api.twitter.com'
    )

    print 'Loading follow list...'
    try:
        follows = []
        next_cursor = -1
        while 1:
            print '.'
            tf = twitter_stream.friends.list(cursor=next_cursor)

            if not tf:
                break

            follows += tf['users']

            if not tf['next_cursor']:
                break

            next_cursor = tf['next_cursor']

    except urllib2.URLError as e:
        print 'ERROR: %s' % e.reason
        return

    except twitter.TwitterError as e:
        print 'ERROR: Twitter sent HTTP status code %d' % e.e.code
        return


    t = {}
    c.execute("SELECT user, COUNT(tweetid) FROM ratings WHERE retweet IS NULL GROUP BY user ORDER BY user")
    t['totals'] = c.fetchall()

    c.execute("SELECT user, COUNT(tweetid) FROM ratings WHERE retweet IS NULL AND timestamp IS NOT NULL GROUP BY user ORDER BY user")
    t['timed'] = c.fetchall()

    c.execute("SELECT user, COUNT(tweetid) FROM ratings WHERE retweet IS NULL AND rating = 2 GROUP BY user ORDER BY user")
    t['good'] = c.fetchall()

    c.execute("SELECT user, COUNT(tweetid) FROM ratings WHERE retweet IS NULL AND rating = 0 GROUP BY user ORDER BY user")
    t['bad'] = c.fetchall()

    c.execute("SELECT user, MIN(timestamp) FROM ratings WHERE retweet IS NULL GROUP BY user ORDER BY user")
    t['oldest'] = c.fetchall()

    c.execute("SELECT user, MAX(timestamp) FROM ratings WHERE retweet IS NULL GROUP BY user ORDER BY user")
    t['newest'] = c.fetchall()

    datatypes = t.keys()
    u = {}

    for dt in datatypes:
        u[dt] = {}

        for record in t[dt]:
            u[dt][record[0]] = record[1]


    table = outputty.Table(headers=['Handle', 'Total', 'Good', 'Bad', 'Newest', 'Oldest', 'Tweets/day', 'Profile'])

    for follow in follows:
        user = follow['screen_name']

        if user in u['totals']:
            total = float(u['totals'][user])
        else:
            total = 0

        if user in u['timed']:
            timed = float(u['timed'][user])
        else:
            timed = 0

        if user in u['good']:
            g = float(u['good'][user])
        else:
            g = 0.0

        if user in u['bad']:
            b = float(u['bad'][user])
        else:
            b = 0.0

        if user in u['newest'] and u['newest'][user] > 0:
            n = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(u['newest'][user])))
        else:
            n = ''

        if user in u['oldest'] and u['oldest'][user] > 0:
            o = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(u['oldest'][user])))
        else:
            o = ''

        if o and timed > 1:
            t = timed / ((time.time() - int(u['oldest'][user])) / (60*60*24))
        else:
            t = 0

        percentgood = 0
        if g and t:
            percentgood = int((g/total) * 100)

        percentbad = 0
        if b and t:
            percentbad = int((b/total) * 100)

        table.append((user, int(total), '%d%%' % percentgood, '%d%%' % percentbad, n, o, round(t), 'http://twitter.com/%s' % user))

    table.order_by('Tweets/day', 'descending')
    print table
    print

    # People you should follow (that don't currently)
    t = {}
    c.execute("SELECT user, COUNT(tweetid) FROM ratings WHERE retweet = 1 GROUP BY user HAVING COUNT(tweetid) > 1 ORDER BY user")
    t['totals'] = c.fetchall()

    c.execute("SELECT user, COUNT(tweetid) FROM ratings WHERE retweet = 1 AND rating = 2 GROUP BY user ORDER BY user")
    t['good'] = c.fetchall()

    c.execute("SELECT user, COUNT(tweetid) FROM ratings WHERE retweet = 1 AND rating = 0 GROUP BY user ORDER BY user")
    t['bad'] = c.fetchall()

    datatypes = t.keys()
    r = {}

    for dt in datatypes:
        r[dt] = {}

        for record in t[dt]:
            r[dt][record[0]] = record[1]


    print 'People you should follow:'
    table = outputty.Table(headers=['Handle', 'Total', 'Good', 'Bad', 'Profile'])

    for user in r['totals']:
        # Check if already followed
        if user in u['totals']:
            continue

        total = float(r['totals'][user])

        if user in r['good']:
            g = float(r['good'][user])
        else:
            g = 0.0

        if user in r['bad']:
            b = float(r['bad'][user])
        else:
            b = 0.0

        table.append((user, int(total), '%d%%' % int((g/total) * 100), '%d%%' % int((b/total) * 100), 'http://twitter.com/%s' % user))

    table.order_by('Good', 'descending')
    print table

main()
