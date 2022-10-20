import sqlite3

connection = sqlite3.Connection('transit_data.db')
cursor = connection.cursor()

# cursor.execute("""
#     UPDATE ESTIMATES
#     SET ETA = 0
#     WHERE ETA = 'DUE'
#     """)

cursor.execute("SELECT COUNT(ID) FROM ESTIMATES WHERE ETA = 'DUE' ORDER BY ETA DESC")
result = cursor.fetchall()
for r in result:
    print(r)

connection.commit()
