import twitter
import shutil
import sys, tty, termios, os
import sqlite3
import config

def main():

    if len(sys.argv) > 1:
         print 'Get tweets before %s' % sys.argv[1]
         max_id = sys.argv[1]
    else:
        max_id = ''

    print 'Backup database...'
    shutil.copyfile('data.db', 'data.db.bak')

    print 'Load database...'
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # Create table
#    c.execute('''CREATE TABLE ratings (tweetid text, user text, rating integer)''')

    # Save (commit) the changes
#    conn.commit()

    print 'Authenticating...'

    twitter_stream = twitter.Twitter(
            auth=config.auth,
            secure=1,
            api_version='1.1',
            domain='api.twitter.com'
    )

    print 'Loading tweets...'
    if max_id:
        iterator = twitter_stream.statuses.home_timeline(count=200, max_id=max_id)
    else:
        iterator = twitter_stream.statuses.home_timeline(count=200)

    if iterator:
        for tweet in iterator:
            handle = tweet['user']['screen_name'].strip()

            name = tweet['user']['name'].strip()

            location = tweet['user']['location'].strip()
            if location:
                location = ' - '+location

            text = tweet['text']

            retweet = ('[RT %]' % tweet['retweeted']) if tweet['retweeted'] else ''

            reply = ('[Reply to %s]' % tweet['in_reply_to_status_id']) if tweet['in_reply_to_status_id'] else ''

            tweet_id = tweet['id_str']

            timestamp = tweet['created_at']

            # Get ratings
            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE rating = 2 AND user = ?", [handle])
            good = c.fetchone()[0]

            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE rating = 0 AND user = ?", [handle])
            bad = c.fetchone()[0]

            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE user = ?", [handle])
            count = c.fetchone()[0]

            # Check if seen
            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE tweetid = ?", [tweet_id])
            seen = c.fetchone()[0]

            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            RED = '\033[91m'
            ORANGE = '\033[93m'
            ENDC = '\033[0m'

            print ''

            if seen:
                print '%s[[SEEN]]%s' % (RED, ENDC)

            print '%s%s %s(%s%s) %s%s%s' % (OKBLUE, handle, OKGREEN, name, location, retweet, reply, ENDC)
            print '%s' % text

            if good:
                good = '%s%s%s' % (OKGREEN, good, ENDC)

            if bad:
                bad = '%s%s%s' % (RED, bad, ENDC)

            print '%s %s/%s/%s %s' % (tweet_id, bad, count, good, timestamp)

            while 1:
                i = handle_input()
                if i in ('q', 'next', 'good', 'bad'):
                    break

            if i == 'q':
                break
            elif i in ('good', 'bad', 'next'):
                if seen:
                    print 'Already seen!'
                    continue

                if i != 'next':
                    print 'Marked as %s' % i

                if i == 'good':
                    rating = 2
                elif i == 'bad':
                    rating = 0
                else:
                    rating = 1

                # Insert a row of data
                c.execute("INSERT INTO ratings VALUES (?, ?, ?)", [tweet_id, handle, rating])
                conn.commit()
                continue

        if i != 'q':
            iterator = twitter_stream.statuses.home_timeline(count=200, max_id=tweet_id)

    conn.close()


def get_input():
    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        while 1:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(3)

            if not ch:
                continue

            break

    except KeyboardInterrupt:
        ch = 'q'

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch[-1]


def handle_input():
    ch = get_input()
    c = ch.lower()

    if c == 'q':
        return 'q'
    elif ord(c) == 98:
        return 'next'
    elif ord(c) == 99:
        return 'good'
    elif ord(c) == 100:
        return 'bad'
    else:
        print ord(c)
        return 'unknown'


main()
