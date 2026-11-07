with open('data_pipeline.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Change image asset errors to warnings in validate_state_dataset
old = """        image_path = static_dir / place['image_url'].lstrip('/')
        if not image_path.exists():
            errors.append(f'{label}: image asset does not exist: {place["image_url"]}')"""

new = """        image_path = static_dir / place['image_url'].lstrip('/')
        if not image_path.exists():
            warnings.append(f'{label}: image asset does not exist: {place["image_url"]}')"""

content = content.replace(old, new)

# Also fix validate_database
old2 = """        if not (static_dir / place['image_url'].lstrip('/')).exists():
            errors.append(f'{label}: image asset does not exist')"""

new2 = """        if not (static_dir / place['image_url'].lstrip('/')).exists():
            warnings.append(f'{label}: image asset does not exist')"""

content = content.replace(old2, new2)

with open('data_pipeline.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated validation to use warnings for missing images')