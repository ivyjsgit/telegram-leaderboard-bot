import sqlite3

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
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
        return(f"{xp}/{total_xp}")
    except:
        return "Max rank!"

def get_user_title(conn, user_id, group_id): 
    c = conn.cursor()
    xp = get_user_xp(conn, user_id, group_id)
    c.execute('SELECT * FROM Titles Where GroupID=? AND MinXP<=? ORDER BY MinXP DESC', (group_id, xp))
    return(c.fetchone()[0])

def create_rank(conn, title, group_id, min_xp):
    c = conn.cursor()
    c.execute('INSERT INTO Titles (Title, GroupID, MinXP) VALUES (?, ?, ?)', (title, group_id, min_xp))
    conn.commit()

def set_xp(conn, user_id, group_id, xp):
    c = conn.cursor()
    c.execute('UPDATE Users Set XP = ? WHERE UserID=? AND GroupID=?', (xp, user_id, group_id))
    conn.commit()
    
connection = create_connection("database.db")
# create_rank(connection, "Test rank", 1, 100000000)
# print(get_user_progress(connection, 1,1))
