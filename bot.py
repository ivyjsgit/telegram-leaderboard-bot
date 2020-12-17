from telegram import Update, User, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import database
import sqlite3
import random

def start(update: Update, context: CallbackContext***REMOVED*** -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Add me to a group to use me!'***REMOVED***

def help(update: Update, context: CallbackContext***REMOVED*** -> None:
    update.message.reply_markdown_v2(f"""Commands: \n /createrank rankname xp: Creates a new rank for the group is is rank in\. Must be ran by an admin\. \n
    /progress: Checks your current title and XP progress\n
    /help: Displays this message\n
    /leaderboard: Displays the users with the top 10 xp in the current group\."""***REMOVED***

def get_progress(update: Update, context: CallbackContext***REMOVED*** -> None:
    conn = database.create_connection("database.db"***REMOVED***
    user_id = update.message.from_user.id
    group_id = update.message.chat.id
    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"

    if group_chat:
        database.create_user_if_not_exists(conn, user_id, group_id***REMOVED***
        progress = database.get_user_progress(conn, user_id, group_id***REMOVED***
        if progress == (-1,-1***REMOVED***:
            xp = database.get_user_xp(conn, user_id, group_id***REMOVED***
            title = database.get_user_title(conn, user_id, group_id***REMOVED***
            update.message.reply_text(f'You are max rank! Your current XP is {xp}. Your title is {title}'***REMOVED***
        else:
            xp, max_xp = database.get_user_progress(conn, user_id, group_id***REMOVED***
            title = database.get_user_title(conn, user_id, group_id***REMOVED***
            update.message.reply_text(f'You are rank {title}! Your current XP is {xp}/{max_xp}!'***REMOVED***
    else:
        update.message.reply_text(f'This command must be run in a group!'***REMOVED***
        
#Adds a rank to the current server. Only works if the user is an admin. Format is /addrank [title] [min_xp]
def add_rank(update: Update, context: CallbackContext***REMOVED*** -> None:
    connection = database.create_connection("database.db"***REMOVED***
    text = context.args
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

def add_xp(update: Update, context: CallbackContext***REMOVED*** -> None:
    conn = database.create_connection("database.db"***REMOVED***
    user_id = update.message.from_user.id
    group_id = update.message.chat.id

    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"

    if group_chat:
        database.create_user_if_not_exists(conn, user_id, group_id***REMOVED***
        progress = database.get_user_progress(conn, user_id, group_id***REMOVED***

        current_xp = database.get_user_xp(conn, user_id, group_id***REMOVED***
        random_xp = random.randint(0, 10***REMOVED***
        new_xp = current_xp+random_xp
        # update.message.reply_text(f'Current XP: {current_xp}, New XP: {new_xp}'***REMOVED***         
        database.set_xp(conn, user_id, group_id, new_xp***REMOVED***

        if progress != (-1, -1***REMOVED***:
            if new_xp>= progress[1]:
                title = database.get_user_title(conn, user_id, group_id***REMOVED***
                user_name = update.message.from_user.full_name
                update.message.reply_text(f'{user_name} has ranked up! They are now rank {title}!'***REMOVED*** 
    else:
        update.message.reply_text(f'Error: can\'t do ranking because not a groupchat'***REMOVED***         

def show_leaderboard(update: Update, context: CallbackContext***REMOVED*** -> None:
    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"
    if group_chat:
        conn = database.create_connection("database.db"***REMOVED***
        group_id = update.message.chat.id
        top_users = database.get_top_users(conn, group_id***REMOVED***
        output = ""
        for user,xp in top_users:
            name = context.bot.get_chat_member(group_id, user***REMOVED***.user.full_name
            title = database.get_user_title(conn, user, group_id***REMOVED***
            curline = f"{name} ({title}***REMOVED*** {xp}xp\n"
            output+=curline
        update.message.reply_text(output***REMOVED***
    else:
        update.message.reply_text("This command must be used in a group!"***REMOVED***

def read_token(filename***REMOVED***:
    f = open(filename, "r"***REMOVED***
    return(f.readline(***REMOVED******REMOVED***

def main(***REMOVED***:
    """Start the bot."""
    updater = Updater(read_token("token"***REMOVED***, use_context=True***REMOVED***

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start***REMOVED******REMOVED***
    dispatcher.add_handler(CommandHandler("help", help***REMOVED******REMOVED***
    dispatcher.add_handler(CommandHandler("progress", get_progress***REMOVED******REMOVED***
    dispatcher.add_handler(CommandHandler("leaderboard", show_leaderboard***REMOVED******REMOVED***
    dispatcher.add_handler(CommandHandler("addrank", add_rank, pass_args=True***REMOVED******REMOVED***

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, add_xp***REMOVED******REMOVED***

    # Start the Bot
    updater.start_polling(***REMOVED***

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling(***REMOVED*** is non-blocking and will stop the bot gracefully.
    updater.idle(***REMOVED***


if __name__ == '__main__':
    main(***REMOVED***