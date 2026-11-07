import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

# Update Amber Fort practical_notes to remove incorrect elephant ride prohibition
# Per audit: elephant rides resumed at Amber Fort on 17 September 2025
# Remove the categorical prohibition claim

db.execute("""
    UPDATE places 
    SET practical_notes = 'Open daily 8:00 AM to 5:30 PM as published by the Rajasthan Tourism department; ticket counters typically close by 5:00 PM. The evening light & sound show at the fort runs on seasonal evening slots (from around 6:30 PM in winter) -- confirm show timings on the day, as they vary by season and language. Tickets: ₹100 for Indian nationals, ₹500 for foreign visitors (composite tickets available). Licensed guides available at Suraj Pol gate.'
    WHERE slug = 'amber-fort'
""")

db.commit()

# Verify the update
r = db.execute("SELECT * FROM places WHERE slug='amber-fort'").fetchall()
for x in r:
    pn = str(x[9])
    print("Updated practical_notes:", pn[:500])

db.close()
print("\nAmber Fort practical_notes updated successfully")