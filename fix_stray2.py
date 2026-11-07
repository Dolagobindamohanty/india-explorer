with open('seed.py', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')
lines = content.split('\n')

# Remove the stray comma at line 574 (index 573)
if lines[573].strip() == ',':
    lines[573] = ''
    print("Removed stray comma at line 574")
else:
    print(f"Line 574 content: '{lines[573][:50]}...'")

# Join back
new_content = '\n'.join(lines)

with open('seed.py', 'wb') as f:
    f.write('\n'.join(lines).encode('utf-8'))

print("Fixed stray comma at line 574")