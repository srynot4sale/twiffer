Twiffer
=======

Twiffer is a minimalistic Twitter shell client. It forces you to rate
each tweet as you view it allowing you to build up statistics
regarding your followed user's signal-to-noise ratios.

The goal of using this client over others is to help "tune" your follow
list so you can spend less time checking Twitter, and at the same time
hopefully get more from it.

Twiffer can be launched by running twiffer.py. Stats can be reviewed
by running stats.py.

Tweets are rated/navigated by using the arrow keys:

* Down: OK tweet
* Right: Good - a useful/thought provoking/entertaining tweet.
* Left: Bad - I gained nothing from this tweet

Pressing q will leave the application.


Screenshot!
-----------

    $ ./twiffer.py
    Create backup of database...
    Load database...
    Checking if database needs setting up...
    Authenticating...
    Get last tweet read...
    Loading tweets...
    Loaded 5 tweets...

    aza (Aza Raskin - San Francisco)
    My heart grieves for Aaron Swartz. He was a leader in the most important type of mischief: that which pushes society forward thoughtfully
    290743186941419520 0/0/0 Mon Jan 14 08:52:32 +0000 2013
    Marked as good

    maberdour (Mark Aberdour - Brighton, UK)
    My new blog post about mobile apps for Moodle: http://t.co/eDMQUOKy
    290746569802801152 0/0/0 Mon Jan 14 09:05:58 +0000 2013

    mattsachtler (Matt Sachtler - Redondo Beach, CA)
    raspbmc : fairly crash-y. not sure if it's xbmc or the pi to blame, but i'm growing frustrated quickly.
    290747002000662529 0/1/0 Mon Jan 14 09:07:41 +0000 2013

    ranginui (Chris Cormack - Wellington, NZ)
    “I Want To Take You Higher” by Sly &amp; The Family Stone is my new jam.  ♫ http://t.co/5r9k9dHT
    290749697927282688 0/9/1 Mon Jan 14 09:18:24 +0000 2013

    dakami (Dan Kaminsky - The Internets)
    RT @hdmoore: Oracle is switching Java security settings to “high” by default: https://t.co/CnOvwklm &lt; All applets now require a click ...
    290753525007384577 0/13/4 Mon Jan 14 09:33:36 +0000 2013


Installation
------------

Twiffer's only requirement is the Python Twitter Tools library. This
library can be installed running the command

    easy_install twitter


Config
------

A config file is required to be created in order to use this client.
Create a file named config.py in the same directory as twiffer.py.

Twiffer expects this file to contain a variable named auth that
contains authentication details.

Here is an example config file. Replace capitilised variables with
your own data.

    import twitter
    auth = twitter.OAuth(
                OAUTH_TOKEN, OAUTH_SECRET,
                CONSUMER_KEY, CONSUMER_SECRET
    )


Getting your OAuth details
--------------------------

Visit the Twitter developer page and create a new application:

    https://dev.twitter.com/apps/new

This will get you a CONSUMER_KEY and CONSUMER_SECRET.

Performing the "oauth dance" gets you an OAUTH_TOKEN and OAUTH_SECRET
that authenticate yourself with Twitter.


License
=======

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
