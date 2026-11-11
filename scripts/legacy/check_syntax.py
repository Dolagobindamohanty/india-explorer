with open('seed.py', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')
lines = content.split('\n')

# Check lines 570-585
with open('check_output.txt', 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines[570:585], start=570):
        safe_line = line.encode('ascii', errors='replace').decode('ascii')
        out.write(f'{i}: {line.rstrip()}\n')

# Check for stray commas
with open('check_output2.txt', 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == ',':
            out.write(f"Stray comma at line {i+1}: '{line}'\n")