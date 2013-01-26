Twiffer
=======

Twiffer is a minimalistic Twitter shell client. It forces you to rate
each tweet as you view it allowing you to build up statistics
regarding your followed user's signal-to-noise ratios.

The goal of using this client over others is to help "tune" your follow
list so you can spend less time checking Twitter, and at the same time
hopefully get more from it.

Another feature of gathering statistics is the ability to find new
user's to follow by how you have rated their tweets that had appeared
due to being retweeted by someone you currently follow.

Twiffer can be launched by running twiffer.py. Stats can be reviewed
by running stats.py.

Tweets are rated/navigated by using the arrow keys:

* Down: OK tweet
* Right: Good - a useful/thought provoking/entertaining tweet.
* Left: Bad - I gained nothing from this tweet

Pressing q will leave the application. Pressing 'up' will let you return
to a tweet to change it's rating.


Screenshot!
-----------

![Screenshot](http://i.imgur.com/O2Ugg2Q.png)


Installation
------------

Twiffer's only requirements are the Python Twitter Tools and Outputty
python libraries. These can be installed with easy_install:

    easy_install twitter outputty


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
