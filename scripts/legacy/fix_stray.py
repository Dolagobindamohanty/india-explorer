with open('seed.py', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')
lines = content.split('\n')

# Check line 573 (index 572)
line_573 = lines[572]
safe = line_573.encode('ascii', errors='replace').decode('ascii')
print(f"Line 573: '{safe}'")

# Fix - remove stray comma line if it's just a comma
if lines[572].strip() == ',':
    lines[572] = ''
    print("Removed stray comma at line 573")
else:
    safe = lines[572].encode('ascii', errors='replace').decode('ascii')
    print(f"Line 573 content: '{safe}'")

# Join back
new_content = '\n'.join(lines)

with open('seed.py', 'wb') as f:
    f.write('\n'.join(lines).encode('utf-8'))

print("Fixed")