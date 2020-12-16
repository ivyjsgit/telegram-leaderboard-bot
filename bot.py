from telegram import Update, User
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import database
import sqlite3
import random

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_markdown_v2(f"""Commands: \n /createrank rankname xp: Creates a new rank for the group is is rank in\. Must be ran by an admin\. \n
    /progress: Checks your current title and XP progress\n
    /help: Displays this message""")

def get_progress(update: Update, context: CallbackContext) -> None:
    conn = database.create_connection("database.db")
    user_id = update.message.from_user.id
    group_id = update.message.chat.id
    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"

    if group_chat:
        database.create_user_if_not_exists(conn, user_id, group_id)
        progress = database.get_user_progress(conn, user_id, group_id)
        if progress == (-1,-1):
            xp = database.get_user_xp(conn, user_id, group_id)
            title = database.get_user_title(conn, user_id, group_id)
            update.message.reply_text(f'You are max rank! Your current XP is {xp}. Your title is {title}')
        else:
            xp, max_xp = database.get_user_progress(conn, user_id, group_id)
            title = database.get_user_title(conn, user_id, group_id)
            update.message.reply_text(f'You are rank {title}! Your current XP is {xp}/{max_xp}!')

#Adds a rank to the current server. Only works if the user is an admin. Format is /addrank [title] [min_xp]
def add_rank(update: Update, context: CallbackContext) -> None:
    connection = database.create_connection("database.db")
    text = update.message.text.split()[1:]
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    admins = update.message.chat.get_administrators()
    admin_user_ids = list(map((lambda chatMember: chatMember.user.id), admins))

    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"
    if group_chat and user_id in admin_user_ids:
        if len(text)>=2:
            title = text[0]
            min_xp = text[1]
            try:
                database.create_rank(connection,title,chat_id,min_xp)
                update.message.reply_text(f'Created rank!')
            except sqlite3.IntegrityError as e:
                update.message.reply_markdown_v2(f'Failed to create rank: rank already exists! \n```{e}```')
            except Exception as e:
                update.message.reply_markdown_v2(f'Failed to create rank: \n```{e}```')
    elif group_chat:
       update.message.reply_text(f'You aren\'t admin!') 
    else:
        update.message.reply_text(f'This command must be ran in a group!')
    connection.close()

def add_xp(update: Update, context: CallbackContext) -> None:
    conn = database.create_connection("database.db")
    user_id = update.message.from_user.id
    group_id = update.message.chat.id

    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"

    if group_chat:
        database.create_user_if_not_exists(conn, user_id, group_id)
        progress = database.get_user_progress(conn, user_id, group_id)

        current_xp = database.get_user_xp(conn, user_id, group_id)
        random_xp = random.randint(0, 10)
        new_xp = current_xp+random_xp
        # update.message.reply_text(f'Current XP: {current_xp}, New XP: {new_xp}')         
        database.set_xp(conn, user_id, group_id, new_xp)

        if progress != (-1, -1):
            if new_xp>= progress[1]:
                title = database.get_user_title(conn, user_id, group_id)
                user_name = update.message.from_user.full_name
                update.message.reply_text(f'{user_name} has ranked up! They are now rank {title}!') 
    else:
        update.message.reply_text(f'Error: can\'t do ranking because not a groupchat')         

# def show_leaderboard(update: Update, context: CallbackContext) -> None:
#     conn = database.create_connection("database.db")
#     group_id = update.message.chat.id
#     top_users = database.get_top_users(conn, group_id)
#     for user in top_users:

#This method is called each time a user sends a message. It will handle giving XP to users.
def read_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat
    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"
    if group_chat:
        update.message.reply_text(f'Read a message from groupchat! user_id: {user_id} group_id: {chat_id.id}')
    else:
        update.message.reply_text(f'Read a message from DM! user_id: {user_id }')

def read_token(filename):
    f = open(filename, "r")
    return(f.readline())

def main():
    """Start the bot."""
    updater = Updater(read_token("token"), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("progress", get_progress))
    dispatcher.add_handler(CommandHandler("addrank", add_rank))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, add_xp))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()