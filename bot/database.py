import sqlite3
import random
import sys

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except:
        e = sys.exc_info()[0]
        print(e)
    return conn

def get_user_xp(conn, user_id, group_id):
    c = conn.cursor()
    c.execute('SELECT * FROM Users WHERE UserID=? AND GroupID=?', (user_id, group_id))
    return(c.fetchone()[2])

def get_user_progress(conn, user_id, group_id): 
    c = conn.cursor()
    xp = get_user_xp(conn, user_id, group_id)
    c.execute('SELECT * FROM Titles Where GroupID=? AND MinXP>? ORDER BY MinXP ASC', (group_id, xp))
    try:
        total_xp=c.fetchone()[2]
        return(xp, total_xp)
    except:
        return (-1,-1)

def get_user_title(conn, user_id, group_id): 
    c = conn.cursor()
    xp = get_user_xp(conn, user_id, group_id)
    c.execute('SELECT * FROM Titles Where GroupID=? AND MinXP<=? ORDER BY MinXP DESC', (group_id, xp))
    result = c.fetchone()
    if result == None:
        return "🌳"
    else:
        return(result[0])

def create_rank(conn, title, group_id, min_xp):
    c = conn.cursor()
    c.execute('INSERT INTO Titles (Title, GroupID, MinXP) VALUES (?, ?, ?)', (title, group_id, min_xp))
    conn.commit()

def set_xp(conn, user_id, group_id, xp):
    c = conn.cursor()
    c.execute('UPDATE Users Set XP = ? WHERE UserID=? AND GroupID=?', (xp, user_id, group_id))
    conn.commit()

def create_user_if_not_exists(conn, user_id, group_id):
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE UserID=? AND GROUPID=?",(user_id, group_id))
    if c.fetchone() == None:
        print(f"User does not exist! {user_id}, {group_id}")
        c.execute("INSERT INTO Users (UserID, GroupID, XP) VALUES (?, ?, ?)", (user_id, group_id, 0))
        conn.commit()

def opt_out(conn, user_id):
    c = conn.cursor()
    c.execute('UPDATE Users Set OptedOut = ? WHERE UserID=?', (True, user_id))
    conn.commit()

def opt_in(conn, user_id):
    c = conn.cursor()
    c.execute('UPDATE Users Set OptedOut = ? WHERE UserID=?', (False, user_id))
    conn.commit()

def get_opt_out_status(conn, user_id) -> bool:
    c = conn.cursor()
    c.execute('SELECT OptedOut FROM Users WHERE UserID=?', (user_id,))
    results =  c.fetchone()
    return bool(results[0])


def get_top_users(conn, group_id): 
    c = conn.cursor()
    c.execute("SELECT UserID, XP FROM Users WHERE GroupID=? ORDER BY XP DESC LIMIT 10", (group_id,))
    return c.fetchall()

def get_titles(conn, group_id):
    c = conn.cursor()
    c.execute("SELECT Title, MinXP FROM Titles WHERE GroupID=? ORDER BY MinXP DESC", (group_id,))
    return c.fetchall()

connection = create_connection("database.db")
# create_user_if_not_exists(connection, 1, 20)

