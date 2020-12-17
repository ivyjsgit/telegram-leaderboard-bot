import sqlite3
import random

def create_connection(db_file***REMOVED***:
    conn = None
    try:
        conn = sqlite3.connect(db_file***REMOVED***
    except Error as e:
        print(e***REMOVED***
    return conn

def get_user_xp(conn, user_id, group_id***REMOVED***:
    c = conn.cursor(***REMOVED***
    c.execute('SELECT * FROM Users WHERE UserID=? AND GroupID=?', (user_id, group_id***REMOVED******REMOVED***
    return(c.fetchone(***REMOVED***[2]***REMOVED***

def get_user_progress(conn, user_id, group_id***REMOVED***: 
    c = conn.cursor(***REMOVED***
    xp = get_user_xp(conn, user_id, group_id***REMOVED***
    c.execute('SELECT * FROM Titles Where GroupID=? AND MinXP>? ORDER BY MinXP ASC', (group_id, xp***REMOVED******REMOVED***
    try:
        total_xp=c.fetchone(***REMOVED***[2]
        return(xp, total_xp***REMOVED***
    except:
        return (-1,-1***REMOVED***

def get_user_title(conn, user_id, group_id***REMOVED***: 
    c = conn.cursor(***REMOVED***
    xp = get_user_xp(conn, user_id, group_id***REMOVED***
    c.execute('SELECT * FROM Titles Where GroupID=? AND MinXP<=? ORDER BY MinXP DESC', (group_id, xp***REMOVED******REMOVED***
    result = c.fetchone(***REMOVED***
    if result == None:
        return "🌳"
    else:
        return(result[0]***REMOVED***

def create_rank(conn, title, group_id, min_xp***REMOVED***:
    c = conn.cursor(***REMOVED***
    c.execute('INSERT INTO Titles (Title, GroupID, MinXP***REMOVED*** VALUES (?, ?, ?***REMOVED***', (title, group_id, min_xp***REMOVED******REMOVED***
    conn.commit(***REMOVED***

def set_xp(conn, user_id, group_id, xp***REMOVED***:
    c = conn.cursor(***REMOVED***
    c.execute('UPDATE Users Set XP = ? WHERE UserID=? AND GroupID=?', (xp, user_id, group_id***REMOVED******REMOVED***
    conn.commit(***REMOVED***

def create_user_if_not_exists(conn, user_id, group_id***REMOVED***:
    c = conn.cursor(***REMOVED***
    c.execute("SELECT * FROM Users WHERE UserID=? AND GROUPID=?",(user_id, group_id***REMOVED******REMOVED***
    if c.fetchone(***REMOVED*** == None:
        c.execute("INSERT INTO Users (UserID, GroupID, XP***REMOVED*** VALUES (?, ?, ?***REMOVED***", (user_id, group_id, 0***REMOVED******REMOVED***
        conn.commit(***REMOVED***

def get_top_users(conn, group_id***REMOVED***: 
    c = conn.cursor(***REMOVED***
    c.execute("SELECT UserID, XP FROM Users WHERE GroupID=? ORDER BY XP DESC LIMIT 10", (group_id,***REMOVED******REMOVED***
    return c.fetchall(***REMOVED***

def get_titles(conn, group_id***REMOVED***:
    c = conn.cursor(***REMOVED***
    c.execute("SELECT Title, MinXP FROM Titles WHERE GroupID=? ORDER BY MinXP DESC", (group_id,***REMOVED******REMOVED***
    return c.fetchall(***REMOVED***

connection = create_connection("database.db"***REMOVED***
# create_user_if_not_exists(connection, 1, 20***REMOVED***

