import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
r = db.execute("SELECT * FROM places WHERE slug='amber-fort'").fetchall()
for x in r:
    pn = str(x[9])
    with open('pn_verify.txt', 'w', encoding='utf-8') as f:
        f.write("practical_notes: " + pn[:500] if len(pn) > 500 else pn)
db.close()
print("Done - verified and saved to pn_verify.txt")