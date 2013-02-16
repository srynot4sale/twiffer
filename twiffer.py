#!/usr/bin/python

import twitter
import calendar, os, shutil, sqlite3, sys, termios, time, tty, urllib2
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
        c.execute('''CREATE TABLE ratings (tweetid text, user text, rating integer, timestamp text, retweet integer)''')
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
    tweet_id = result[0] if result else 0

    print 'Loading tweets...'
    try:
        tweets = []
        max_id = None
        while 1:
            if max_id:
                page = twitter_stream.statuses.home_timeline(count=200, since_id=tweet_id, max_id=max_id)
            else:
                page = twitter_stream.statuses.home_timeline(count=200, since_id=tweet_id)

            tweets += page
            if len(page) == 0:
                break

            max_id = tweets[-1]['id'] - 1

    except urllib2.URLError as e:
        print 'ERROR: %s' % e.reason
        return
    except twitter.TwitterError as e:
        print 'ERROR: Twitter sent HTTP status code %d' % e.e.code
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

            # Get ratings
            ratings = {}
            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE rating = 2 AND user = ?", [handle])
            ratings['good'] = c.fetchone()[0]
            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE rating = 0 AND user = ?", [handle])
            ratings['bad'] = c.fetchone()[0]
            c.execute("SELECT COUNT(tweetid) FROM ratings WHERE user = ?", [handle])
            ratings['count'] = c.fetchone()[0]

            # Check if seen
            c.execute("SELECT rating FROM ratings WHERE tweetid = ?", [tweet_id])
            seen = c.fetchone()

            # Get original tweet if retweet
            retweet = False
            if 'retweeted_status' in tweet:
                retweet = tweet['retweeted_status']
                tweet['text'] = 'RT @%s: %s' % (retweet['user']['screen_name'].strip(), retweet['text'])

            # Display tweet
            print format_tweet(tweet, retweet, seen, ratings, t, total)

            # Wait for input
            i = handle_input()

            if i == 'quit':
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

                timestamp_utc = get_utc_timestamp(tweet['created_at'])

                # Insert/update a row of data
                if seen:
                    c.execute("UPDATE ratings SET rating = ? WHERE tweetid = ?", [rating, tweet_id])
                else:
                    c.execute("INSERT INTO ratings VALUES (?, ?, ?, ?, ?)", [tweet_id, handle, rating, timestamp_utc, None])

                conn.commit()

                # If retweet, insert/update
                if retweet:
                    if seen:
                        c.execute("UPDATE ratings SET rating = ? WHERE tweetid = ?", [rating, retweet['id_str']])
                    else:
                        c.execute("INSERT INTO ratings VALUES (?, ?, ?, ?, ?)", [retweet['id_str'], retweet['user']['screen_name'].strip(), rating, timestamp_utc, 1])

                    conn.commit()

                continue
            elif i == 'previous':
                print 'Go back'
                t -= 2
                continue

        if i == 'quit':
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
            return 'quit'
        elif chars == KEY_UP:
            return 'previous'
        elif chars == KEY_DOWN:
            return 'next'
        elif chars == KEY_RIGHT:
            return 'good'
        elif chars == KEY_LEFT:
            return 'bad'


def get_utc_timestamp(timecreated):
    return calendar.timegm(time.strptime(timecreated,'%a %b %d %H:%M:%S +0000 %Y'))


def format_tweet(tweet, retweet, seen, ratings, count, total):
    tweet_id = tweet['id_str']
    handle = tweet['user']['screen_name'].strip()
    name = tweet['user']['name'].strip()
    text = tweet['text']
    retweeted = ('[RT %d times]' % tweet['retweet_count']) if tweet['retweet_count'] else ''
    reply = ('[Reply to %s] ' % tweet['in_reply_to_status_id']) if tweet['in_reply_to_status_id'] else ''

    location = tweet['user']['location'].strip()
    if location:
        location = ' - '+location

    time_created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(get_utc_timestamp(tweet['created_at'])))

    # Expand links in tweet
    if 'entities' in tweet.keys() and 'urls' in tweet['entities'].keys():
        for url in tweet['entities']['urls']:
            text = text.replace(url['url'], url['expanded_url'])

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'

    display = '\n'

    if seen:
        if seen[0] == 2:
            rating = 'good'
        elif seen[0] == 0:
            rating = 'bad'
        else:
            rating = 'ok'

        display += '%s[[SEEN - rated %s]]%s\n' % (RED, rating, ENDC)

    display += '%s%s %s%s%s %s%s%s\n' % (BLUE, name, GREEN, handle, location, reply, retweeted, ENDC)
    display += '%s\n' % text

    if ratings['good']:
        ratings['good'] = '%s%s%s' % (GREEN, ratings['good'], ENDC)

    if ratings['bad']:
        ratings['bad'] = '%s%s%s' % (RED, ratings['bad'], ENDC)

    display += 'http://twitter.com/%s/status/%s %s/%s/%s %s (%d of %d)' % (
            handle, tweet_id,
            ratings['bad'], ratings['count'], ratings['good'],
            time_created,
            count, total
    )

    return display


main()
