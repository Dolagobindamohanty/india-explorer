with open('seed.py', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')
lines = content.split('\n')

# Search for lines that are just a comma
for i, line in enumerate(lines):
    if line.strip() == ',':
        print(f"Stray comma at line {i+1}")
        # Show context
        for j in range(max(0, i-2), min(len(lines), i+3)):
            safe = lines[j].encode('ascii', errors='replace').decode('ascii')
            print(f"  {j+1}: {lines[j].rstrip()}")