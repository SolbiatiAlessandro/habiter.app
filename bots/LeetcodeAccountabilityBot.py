#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from html import escape

import logging
import threading
import os
from time import sleep
from datetime import datetime
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
import pytz
import psycopg2
import analytics

DATABASE_URL = os.environ['DATABASE_URL']
BOTNAME = "LeetcodeAccountabilityBot"
analytics.write_key = 'KGYQIoNehP4kak6fK24iPfH3i7FTIYht'

TIMEFORMAT = "%a, %d %b %Y, at %H:%M:%S (%z)"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text('Hi! I organise Group Leetcode session on Telegram. Type/leetcode <time> to set a new leetcode session. <time> need to be in the format of '+datetime.utcnow().replace(tzinfo=pytz.utc).strftime(TIMEFORMAT))

LEETCODE_PROBLEMS = ["https://leetcode.com/problems/top-k-frequent-words/", "https://leetcode.com/problems/integer-replacement/","https://leetcode.com/problems/minimum-path-sum/","https://leetcode.com/problems/longest-repeating-character-replacement/","https://leetcode.com/problems/maximum-difference-between-node-and-ancestor/","https://leetcode.com/problems/hand-of-straights/","https://leetcode.com/problems/4sum-ii/","https://leetcode.com/problems/longest-substring-with-at-least-k-repeating-characters/","https://leetcode.com/problems/shuffle-an-array/","https://leetcode.com/problems/insert-delete-getrandom-o1/", "https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/","https://leetcode.com/problems/top-k-frequent-elements/"]


def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Timer finished!')

def run_leetcode_session(context):
    """
    leetcode sesssion
    """
    job = context.job
    context.bot.send_message(job.context, text="Let's start our Leetcode Session! 🔥🔥🔥 These are the problems we are solving, send a screenshot of your solution.")
    context.bot.send_message(job.context, text=LEETCODE_PROBLEMS[10])
    context.bot.send_message(job.context, text=LEETCODE_PROBLEMS[11])


def set_leetcode_session(update, context):
    """Set next event session"""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        string_time = " ".join(context.args)
        logger.warning("Setting a new leetcode session at: {}".format(string_time))

        try:
            session_start_time = datetime.strptime(string_time, TIMEFORMAT)
            now = datetime.utcnow().replace(tzinfo=pytz.utc)
            due = (session_start_time - now).seconds
        except ValueError as e:
            update.message.reply_text("You are setting the time {} with wrong format:".format(string_time))
            update.message.reply_text(e)
            return
        
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue and stop current one if there is a timer already
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        logging.info("next session due in {} seconds".format(due))
        new_job = context.job_queue.run_once(run_leetcode_session, due, context=chat_id)
        context.chat_data['job'] = new_job

        update.message.reply_text('Leetcode Session successfully set for {}'.format(string_time))

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /leetcode <seconds>')


def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue and stop current one if there is a timer already
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_once(alarm, due, context=chat_id)
        context.chat_data['job'] = new_job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

"""FOLLOWING COMES FROM https://github.com/jh0ker/welcomebot/blob/master/bot.py"""
@run_async
def send_async(bot, *args, **kwargs):
    bot.sendMessage(*args, **kwargs);

# Welcome a user to the chat
def welcome(bot, update):
    """ Welcomes a user to the chat """

    message = update.message
    chat_id = message.chat.id
    for member in message.new_chat_members:
        logger.info('%s joined to chat %d (%s)'
                     % (escape(member.first_name),
                        chat_id,
                        escape(message.chat.title)))

        # CALL PSYCOPG2 TO UPDATE DATABASE THAT ONE INVITE
        # HAS BEEN CONFIRMED

        # Use default message if there's no custom one set
        text = 'Hi $username! Please read the pinned post and feel free to introduce yourself.'
        # Replace placeholders and send message
        text = text.replace('$username',
                            member.first_name)\
            .replace('$title', message.chat.title)
        update.message.reply_text(text)

        #update DB that  user joined
        team_name = message.chat.title
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("UPDATE leetcode_teams SET claimed = claimed + 1 WHERE team_name = %s", (team_name, ))
        conn.commit()
        cur.close()
        conn.close()

        analytics.identify(member.id, {
            'first_name': member.first_name,
            'last_name': member.last_name,
        })

        analytics.track(member.id, 'LeetcodeClaimed', {
          'team_name': team_name
        })

        #update.message.reply_text("I am a bit of a crazy bot, here to help. I am happy now that you're here.")


# Welcome a user to the chat
def goodbye(bot, update):
    """ Sends goodbye message when a user left the chat """

    message = update.message
    chat_id = message.chat.id
    logger.info('%s left chat %d (%s)'
                 % (escape(message.left_chat_member.first_name),
                    chat_id,
                    escape(message.chat.title)))

    text = 'Goodbye, $username!'

    # Replace placeholders and send message
    text = text.replace('$username',
                        message.left_chat_member.first_name)\
        .replace('$title', message.chat.title)
    update.message.reply_text(text)

def chat_event(update, bot):
    """
    Empty messages could be status messages, so we check them if there is a new
    group member, someone left the chat or if the bot has been added somewhere.
    """

    """ WE DON'T HAVE A DB
    # Keep chatlist
    chats = db.get('chats')

    if update.message.chat.id not in chats:
        chats.append(update.message.chat.id)
        db.set('chats', chats)
        logger.info("I have been added to %d chats" % len(chats))
    """

    if update.message.new_chat_members:
        logging.info("1")
        # Bot was added to a group chat
        for member in update.message.new_chat_members:
            if member.username == BOTNAME:
                return introduce(bot, update)
        # Another user joined the chat
        else:
            return welcome(bot, update)

    # Someone left the chat
    elif update.message.left_chat_member is not None:
        logging.info("2")
        if update.message.left_chat_member.username != BOTNAME:
            return goodbye(bot, update)

# Introduce the bot to a chat its been added to
def introduce(bot, update):
    """
    Introduces the bot to a chat its been added to and saves the user id of the
    user who invited us.
    """

    chat_id = update.message.chat.id
    invited = update.message.from_user.id

    logger.info('Invited by %s to chat %d (%s)'
                % (invited, chat_id, update.message.chat.title))

    text = 'Hello %s! I will now greet anyone who joins this chat with a' \
           ' nice message \nCheck the /start command for more info!'\
           % (update.message.chat.title)
    update.message.reply_text(text)


def main():
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN="1066043441:AAFj7XoIZoJ_03pYSNTQVK4wr-AxoBZup6k"
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("leetcode", set_leetcode_session,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    #welcome bot taken from https://github.com/jh0ker/welcomebot/blob/master/bot.py
    dp.add_handler(MessageHandler(Filters.status_update, chat_event))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    logger.warning("start polling telegram bot")
    updater.start_polling()

    # was getting this error:
    # File "/app/.heroku/python/lib/python3.7/site-packages/telegram/ext/updater.py", line 577, in idle
    # ValueError: signal only works in main thread
    #
    # that happens cause we are multithreading
    # so I rewrote the .idle function without signal handling

    logger.warning("## bot is running ##")
    updater.is_idle = True
    while updater.is_idle:
        sleep(1)

def run_dummy_server():
    # HACK TO OCCUPY $PORT
    # otherwise heroku complains
    PORT = int(os.environ.get('PORT', '8443'))
    import http.server
    import socketserver

    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logger.warning("starting dummy server at PORT: "+str(PORT))
        httpd.serve_forever()

if __name__ == '__main__':
    t1 = threading.Thread(target=run_dummy_server)
    t2 = threading.Thread(target=main)
    t1.start()
    t2.start()
