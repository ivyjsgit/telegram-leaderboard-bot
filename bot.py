from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import database
import sqlite3

def start(update: Update, context: CallbackContext***REMOVED*** -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!'***REMOVED***

def get_xp(update: Update, context: CallbackContext***REMOVED*** -> None:
    update.message.reply_text('Your XP is....'***REMOVED***

def get_progress(update: Update, context: CallbackContext***REMOVED*** -> None:
    update.message.reply_text('Your progress is....'***REMOVED***

#Adds a rank to the current server. Only works if the user is an admin. Format is /addrank [title] [min_xp]
def add_rank(update: Update, context: CallbackContext***REMOVED*** -> None:
    connection = database.create_connection("database.db"***REMOVED***
    text = update.message.text.split(***REMOVED***[1:]
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    admins = update.message.chat.get_administrators(***REMOVED***
    admin_user_ids = list(map((lambda chatMember: chatMember.user.id***REMOVED***, admins***REMOVED******REMOVED***

    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"
    if group_chat and user_id in admin_user_ids:
        if len(text***REMOVED***>=2:
            title = text[0]
            min_xp = text[1]
            try:
                database.create_rank(connection,title,chat_id,min_xp***REMOVED***
                update.message.reply_text(f'Created rank!'***REMOVED***
            except sqlite3.IntegrityError as e:
                update.message.reply_markdown_v2(f'Failed to create rank: rank already exists! \n```{e}```'***REMOVED***
            except Exception as e:
                update.message.reply_markdown_v2(f'Failed to create rank: \n```{e}```'***REMOVED***
    elif group_chat:
       update.message.reply_text(f'You aren\'t admin!'***REMOVED*** 
    else:
        update.message.reply_text(f'This command must be ran in a group!'***REMOVED***
    connection.close(***REMOVED***

#This method is called each time a user sends a message. It will handle giving XP to users.
def read_message(update: Update, context: CallbackContext***REMOVED*** -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat
    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"
    if group_chat:
        update.message.reply_text(f'Read a message from groupchat! user_id: {user_id} group_id: {chat_id.id}'***REMOVED***
    else:
        update.message.reply_text(f'Read a message from DM! user_id: {user_id }'***REMOVED***

def read_token(filename***REMOVED***:
    f = open(filename, "r"***REMOVED***
    return(f.readline(***REMOVED******REMOVED***

def main(***REMOVED***:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(read_token("token"***REMOVED***, use_context=True***REMOVED***

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start***REMOVED******REMOVED***
    dispatcher.add_handler(CommandHandler("progress", get_progress***REMOVED******REMOVED***
    dispatcher.add_handler(CommandHandler("getxp", get_xp***REMOVED******REMOVED***
    dispatcher.add_handler(CommandHandler("addrank", add_rank***REMOVED******REMOVED***

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, read_message***REMOVED******REMOVED***

    # Start the Bot
    updater.start_polling(***REMOVED***

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling(***REMOVED*** is non-blocking and will stop the bot gracefully.
    updater.idle(***REMOVED***


if __name__ == '__main__':
    main(***REMOVED***