import sqlite3

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
        return(f"{xp}/{total_xp}"***REMOVED***
    except:
        return "Max rank!"

def get_user_title(conn, user_id, group_id***REMOVED***: 
    c = conn.cursor(***REMOVED***
    xp = get_user_xp(conn, user_id, group_id***REMOVED***
    c.execute('SELECT * FROM Titles Where GroupID=? AND MinXP<=? ORDER BY MinXP DESC', (group_id, xp***REMOVED******REMOVED***
    return(c.fetchone(***REMOVED***[0]***REMOVED***

def create_rank(conn, title, group_id, min_xp***REMOVED***:
    c = conn.cursor(***REMOVED***
    c.execute('INSERT INTO Titles (Title, GroupID, MinXP***REMOVED*** VALUES (?, ?, ?***REMOVED***', (title, group_id, min_xp***REMOVED******REMOVED***
    conn.commit(***REMOVED***

def set_xp(conn, user_id, group_id, xp***REMOVED***:
    c = conn.cursor(***REMOVED***
    c.execute('UPDATE Users Set XP = ? WHERE UserID=? AND GroupID=?', (xp, user_id, group_id***REMOVED******REMOVED***
    conn.commit(***REMOVED***
    
connection = create_connection("database.db"***REMOVED***
# create_rank(connection, "Test rank", 1, 100000000***REMOVED***
# print(get_user_progress(connection, 1,1***REMOVED******REMOVED***
