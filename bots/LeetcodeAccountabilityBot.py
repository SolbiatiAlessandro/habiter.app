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

import logging
import threading
import os
from time import sleep
from datetime import datetime
from telegram.ext import Updater, CommandHandler


CTIME_FORMAT = "%a %b %d %H:%M:%S %Y"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text('Hi! I organise Group Leetcode session on Telegram. Type/leetcode <time> to set a new leetcode session. <time> need to be in the format of '+datetime.now().ctime())


def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Timer finished!')

def run_leetcode_session(context):
    """
    leetcode sesssion
    """
    job = context.job
    context.bot.send_message(job.context, text='Leetcode Session starting now')

def set_leetcode_session(update, context):
    """Set next event session"""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        string_time = " ".join(context.args)
        logger.warning("Setting a new leetcode session at: {}".format(string_time))

        try:
            session_start_time = datetime.strptime(string_time, CTIME_FORMAT)
            due = (session_start_time - datetime.now()).seconds
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
