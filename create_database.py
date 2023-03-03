import sqlite3

con = sqlite3.connect("data.db")

cur = con.cursor()

cur.execute("CREATE TABLE memo(literal PRIMARY KEY, pron_url, note, img_url)")

res  = cur.execute("select * from sqlite_master where name = 'memo'")
print(res.fetchall())

con.close()
