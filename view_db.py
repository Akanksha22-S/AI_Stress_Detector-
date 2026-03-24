import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

print("\n================ USERS TABLE ================\n")

print("+----+----------------------+------------------------------+------------------+")
print("| ID | Name                 | Email                        | Password         |")
print("+----+----------------------+------------------------------+------------------+")

for row in rows:
    print("| {:<2} | {:<20} | {:<28} | {:<16} |".format(
        row[0], row[1], row[2], row[3]
    ))

print("+----+----------------------+------------------------------+------------------+")

conn.close()
