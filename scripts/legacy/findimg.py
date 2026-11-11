with open('app.py', encoding='utf-8') as f:
    for i,l in enumerate(f,1):
        if 'image' in l.lower():
            print(i, l.rstrip())
