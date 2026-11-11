import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
r = db.execute("SELECT * FROM places WHERE slug='amber-fort'").fetchall()
for x in r:
    pn = str(x[9])
    # Check if "Elephant rides are prohibited" is in the notes
    has_prohibition = "Elephant rides are prohibited" in pn
    print(f"Amber Fort practical_notes contains elephant prohibition: {has_prohibition}")
    print(f"Notes start with: {pn[:100]}...")
db.close()