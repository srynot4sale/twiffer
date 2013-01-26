#!/usr/bin/python

import twitter
import calendar, os, shutil, sys, termios, time, tty, urllib2
import sqlite3
import config

KEY_UP    = [chr(27), chr(91), 'A']
KEY_DOWN  = [chr(27), chr(91), 'B']
KEY_RIGHT = [chr(27), chr(91), 'C']
KEY_LEFT  = [chr(27), chr(91), 'D']

def main():

    db_path = os.path.join(sys.path[0], 'data.db')

    print 'Create backup of database...'
    shutil.copyfile(db_path, db_path+'.bak')

    print 'Load database...'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print 'Checking if database needs setting up...'
    c.execute('SELECT name FROM sqlite_master WHERE type = ? AND name = ?', ['table', 'ratings'])
    if not c.fetchone():
        print 'Setup database...'
        c.execute('''CREATE TABLE ratings (tweetid text, user text, rating integer, timestamp text)''')
        conn.commit()

    print 'Authenticating...'
    twitter_stream = twitter.Twitter(
            auth=config.auth,
            secure=1,
            api_version='1.1',
            domain='api.twitter.com'
    )

    print 'Get last tweet read...'
    c.execute('SELECT MAX(tweetid) FROM ratings')
    result = c.fetchone()
    if result:
        tweet_id = result[0]
    else:
        tweet_id = 0

    print 'Loading tweets...'
    try:
        tweets = twitter_stream.statuses.home_timeline(count=200, since_id=tweet_id)
    except urllib2.URLError as e:
        print 'ERROR: %s' % e.reason
        return

    while tweets:
        tweets.reverse()
        total = len(tweets)

        print 'Loaded %d tweets...' % total

        t = 0
        while t < total:
            tweet = tweets[t]
            t += 1

            tweet_id = tweet['id_str']

            handle = tweet['user']['screen_name'].strip()

            name = tweet['user']['name'].strip()

            location = tweet['user']['location'].strip()
            if location:
                location = ' - '+location

            text = tweet['text']
            truncated = ' [truncated]' if tweet['truncated'] else ''

            retweeted = ('[RT %d times]' % tweet['retweet_count']) if tweet['retweet_count'] else ''
            reply = ('[Reply to %s] ' % tweet['in_reply_to_status_id']) if tweet['in_reply_to_status_id'] else ''

            # Get original tweet if retweet
            retweet = False
            if 'retweeted_status' in tweet:
                retweet = tweet['retweeted_status']
                text = 'RT @%s: %s' % (retweet['user']['screen_name'].strip(), retweet['text'])

            timestamp_utc = calendar.timegm(time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
            time_created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_utc))

            # Get ratings
            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE rating = 2 AND user = ?", [handle])
            good = c.fetchone()[0]

            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE rating = 0 AND user = ?", [handle])
            bad = c.fetchone()[0]

            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE user = ?", [handle])
            count = c.fetchone()[0]

            # Check if seen
            c.execute("SELECT rating FROM ratings WHERE tweetid = ?", [tweet_id])
            seen = c.fetchone()

            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            RED = '\033[91m'
            ORANGE = '\033[93m'
            ENDC = '\033[0m'

            print ''

            if seen:
                if seen[0] == 2:
                    rating = 'good'
                elif seen[0] == 0:
                    rating = 'bad'
                else:
                    rating = 'ok'

                print '%s[[SEEN - rated %s]]%s' % (RED, rating, ENDC)

            print '%s%s %s%s%s %s%s%s' % (OKBLUE, name, OKGREEN, handle, location, reply, retweeted, ENDC)
            print '%s%s' % (text, truncated)

            if good:
                good = '%s%s%s' % (OKGREEN, good, ENDC)

            if bad:
                bad = '%s%s%s' % (RED, bad, ENDC)

            print 'http://twitter.com/%s/status/%s %s/%s/%s %s (%d of %d)' % (handle, tweet_id, bad, count, good, time_created, t, total)

            i = handle_input()

            if i == 'q':
                break
            elif i in ('good', 'bad', 'next'):
                if i != 'next':
                    print 'Marked as %s' % i

                if i == 'good':
                    rating = 2
                elif i == 'bad':
                    rating = 0
                else:
                    rating = 1

                # Insert/update a row of data
                if seen:
                    c.execute("UPDATE ratings SET rating = ? WHERE tweetid = ?", [rating, tweet_id])
                else:
                    c.execute("INSERT INTO ratings VALUES (?, ?, ?, ?)", [tweet_id, handle, rating, timestamp_utc])

                conn.commit()
                continue
            elif i == 'previous':
                print 'Go back'
                t -= 2
                continue

        if i == 'q':
            tweets = None
        else:
            tweets = twitter_stream.statuses.home_timeline(count=200, since_id=tweet_id)
            print ''

    conn.close()


def get_input():

    # Only key presses we will return for (chr(3) is Ctrl-C)
    acceptable_chars = [['q'], ['Q'], [chr(3)], KEY_UP, KEY_LEFT, KEY_RIGHT, KEY_DOWN]

    def get_single_char():
        # Weird code to not echo key input, and to return a byte of input at a time
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

        except Exception:
            ch = 'q'

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch

    chars = []
    while chars not in acceptable_chars and chars[0:-1] not in acceptable_chars:
        chars.append(get_single_char())
        while len(chars) > 3:
            chars.pop(0)

    return chars


def handle_input():
    while 1:
        chars = get_input()

        if chars[-1] in ('q', 'Q', chr(3)):
            return 'q'
        elif chars == KEY_UP:
            return 'previous'
        elif chars == KEY_DOWN:
            return 'next'
        elif chars == KEY_RIGHT:
            return 'good'
        elif chars == KEY_LEFT:
            return 'bad'


main()
