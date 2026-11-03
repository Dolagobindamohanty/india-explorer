import sys

with open('app.py') as f:
    for i,l in enumerate(f,1):
        if 'image' in l.lower():
            print(i,l.rstrip())
