import sqlite3
import datetime

connection = sqlite3.Connection('transit_data.db')
cursor = connection.cursor()

# li = []
# cursor.execute("SELECT ID, TIME_CHECKED, SCRAPE_ID FROM ESTIMATES ORDER BY TIME_CHECKED ASC")
# while cursor.fetchone():
#     li.append(cursor.fetchone())
# print(len(li))

cursor.execute("""
SELECT * FROM ESTIMATES LIMIT 10
""")
r = cursor.fetchall()
for i in r:
    print(i)

connection.commit()
