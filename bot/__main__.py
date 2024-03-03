from telegram import Update, User, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import bot.database as database
import sqlite3
import random
import psutil
import distro

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Add me to a group to use me!')

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_markdown_v2(f"""Commands: \n /createrank rankname xp: Creates a new rank for the group is is rank in\. Must be ran by an admin\. \n
    /progress: Checks your current title and XP progress\n
    /help: Displays this message\n
    /leaderboard: Displays the users with the top 10 xp in the current group\.""")

def get_progress(update: Update, context: CallbackContext) -> None:
    conn = database.create_connection("database.db")
    is_reply = update.message.reply_to_message != None
    user_id =  update.message.reply_to_message.from_user.id if is_reply else update.message.from_user.id
    group_id = update.message.chat.id
    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"

    if group_chat:
        database.create_user_if_not_exists(conn, user_id, group_id)
        is_opted_out = database.get_opt_out_status(conn, user_id)
        progress = database.get_user_progress(conn, user_id, group_id)
        if progress == (-1,-1):
            xp = database.get_user_xp(conn, user_id, group_id)
            title = database.get_user_title(conn, user_id, group_id)
            if is_reply:
                username = update.message.reply_to_message.from_user.full_name
                if is_opted_out:
                    update.message.reply_text(f'{username} is max rank! Their current XP is {xp}. Their title is {title}. They are opted out')
                else:
                    update.message.reply_text(f'{username} is max rank! Their current XP is {xp}. Their title is {title}')
            else:
                if is_opted_out:
                    update.message.reply_text(f'You are max rank! Your current XP is {xp}. Your title is {title}. You are opted out')
                else:
                    update.message.reply_text(f'You are max rank! Your current XP is {xp}. Your title is {title}')
        else:
            xp, max_xp = database.get_user_progress(conn, user_id, group_id)
            title = database.get_user_title(conn, user_id, group_id)
            if is_reply:
                username = update.message.reply_to_message.from_user.full_name
                if is_opted_out:
                    update.message.reply_text(f'{username} is rank {title}! Their current XP is {xp}/{max_xp}! They are opted out.')
                else:
                    update.message.reply_text(f'{username} is rank {title}! Their current XP is {xp}/{max_xp}!')
            else:
                if is_opted_out:
                    update.message.reply_text(f'You are rank {title}! Your current XP is {xp}/{max_xp}! You are opted out.')
                else:
                    update.message.reply_text(f'You are rank {title}! Your current XP is {xp}/{max_xp}!')
    else:
        update.message.reply_text(f'This command must be run in a group!')

#Adds a rank to the current server. Only works if the user is an admin. Format is /addrank [title] [min_xp]
def add_rank(update: Update, context: CallbackContext) -> None:
    connection = database.create_connection("database.db")
    text = context.args
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
    if update.message != None and update.message.from_user != None:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id

        group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"
        if group_chat:
            database.create_user_if_not_exists(conn, user_id, group_id)
            if database.get_opt_out_status(conn, user_id) == False:
                progress = database.get_user_progress(conn, user_id, group_id)

                current_xp = database.get_user_xp(conn, user_id, group_id)
                random_xp = award_xp(update.message.text)
                # update.message.reply_text(f"Your message: {update.message.text} XP given: {random_xp} length: {len(update.message.text)}")
                new_xp = current_xp+random_xp
                database.set_xp(conn, user_id, group_id, new_xp)

                if progress != (-1, -1):
                    if new_xp>= progress[1]:
                        title = database.get_user_title(conn, user_id, group_id)
                        user_name = update.message.from_user.full_name
                        update.message.reply_text(f'{user_name} has ranked up! They are now rank {title}!')

def award_xp(message:str ) -> int:
    if len(message)<=3:
        return random.randint(0, 2)
    else:
        return random.randint(0, 15)

def opt_out_command(update: Update, context: CallbackContext) -> None:
    conn = database.create_connection("database.db")
    if update.message != None and update.message.from_user != None:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id

        group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"

        if group_chat:
            database.create_user_if_not_exists(conn, user_id, group_id)
            database.opt_out(conn, user_id)
            update.message.reply_text(f'You have been opted out!')

def opt_in_command(update: Update, context: CallbackContext) -> None:
    conn = database.create_connection("database.db")
    if update.message != None and update.message.from_user != None:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id

        group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"

        if group_chat:
            database.create_user_if_not_exists(conn, user_id, group_id)
            database.opt_in(conn, user_id)
            update.message.reply_text(f'You have been opted in!')




def show_leaderboard(update: Update, context: CallbackContext) -> None:
    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"
    if group_chat:
        conn = database.create_connection("database.db")
        group_id = update.message.chat.id
        top_users = database.get_top_users(conn, group_id)
        output = ""
        for user,xp in top_users:
            try:
                name = context.bot.get_chat_member(group_id, user).user.full_name
            except:
                print(user)
                name = "Deleted user"
            title = database.get_user_title(conn, user, group_id)
            curline = f"{name} ({title}) {xp}xp\n"
            output+=curline
        update.message.reply_text(output)
    else:
        update.message.reply_text("This command must be used in a group!")

def list_ranks(update: Update, context: CallbackContext) -> None:
    group_chat = update.message.chat.type=="group" or update.message.chat.type=="supergroup"
    if group_chat:
        conn = database.create_connection("database.db")
        group_id = update.message.chat.id
        output = ""
        titles = database.get_titles(conn, group_id)
        count = 1
        for title, xp in titles:
            curline = f"{count}. {title} - {xp}xp\n"
            count+=1
            output+=curline
        update.message.reply_text(output)
    else:
        update.message.reply_text("This command must be used in a group!")

def get_opt_status(update: Update, context: CallbackContext) -> None:
        conn = database.create_connection("database.db")
        user_id = update.message.from_user.id
        status = database.get_opt_out_status(conn, user_id)
        update.message.reply_text(f"Opted out: {status}")

def read_token(filename):
    f = open(filename, "r")
    return(f.readline())

def get_os_version():
    return f"{distro.id().title()} {distro.version(best=True)}"

def get_memory_usage():
    memory = psutil.virtual_memory()
    total_memory = memory.total / (1024 ** 3)  # Convert to GB
    used_memory = memory.used / (1024 ** 3)  # Convert to GB
    return total_memory, used_memory

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_system_info(update: Update, context: CallbackContext):
    user_id =  update.message.from_user.id

    if user_id == 191006256:
        os_version = get_os_version()
        total_memory, used_memory = get_memory_usage()
        cpu_usage = get_cpu_usage()

        message = f"""OS version: {os_version}\n
Memory usage {used_memory: .2f}/{total_memory: .2f}GB\n
CPU usage: {cpu_usage: .2f}%"""
        print(message)
        update.message.reply_text(message)
    else:
        update.message.reply_text("This command can only be ran by the owner of the bot")

def main():
    """Start the bot."""

    print("Bot started!")
    updater = Updater(read_token("token"), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("progress", get_progress))
    dispatcher.add_handler(CommandHandler("leaderboard", show_leaderboard))
    dispatcher.add_handler(CommandHandler("addrank", add_rank, pass_args=True))
    dispatcher.add_handler(CommandHandler("ranks", list_ranks))
    dispatcher.add_handler(CommandHandler("optout", opt_out_command))
    dispatcher.add_handler(CommandHandler("optin", opt_in_command))
    dispatcher.add_handler(CommandHandler("getoptinstatus", get_opt_status))
    dispatcher.add_handler(CommandHandler("sysinfo", get_system_info))
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