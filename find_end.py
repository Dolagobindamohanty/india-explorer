with open('seed.py', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('places = [')
print(f"places list starts at: {start}")

bracket_count = 0
for i, char in enumerate(content[start:], start=start):
    if char == '[':
        bracket_count += 1
    elif char == ']':
        bracket_count -= 1
        if bracket_count == 0:
            print(f"End of places list at: {i}")
            print(f"Context: ...{content[i-50:i+20]}...")
            break