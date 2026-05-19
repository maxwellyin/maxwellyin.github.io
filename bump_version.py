#!/usr/bin/env python3
import os
import re
import datetime

# Generate a unique version string using the current timestamp (e.g., 20260519125500)
new_version = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
print(f"Bumping version query parameters to: ?v={new_version}")

# Regex to find links with version parameters, matching '?v=' followed by alphanumeric characters, dashes, or underscores
version_regex = re.compile(r'(\?v=)[0-9A-Za-z_-]+')

changed_files = 0

for root, dirs, files in os.walk('.'):
    # Ignore venv, git, and other dependency folders
    if any(p in root for p in ['.git', '.venv', 'node_modules']):
        continue
        
    for file in files:
        if file.endswith(('.html', '.css')):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if version_regex.search(content):
                    new_content = version_regex.sub(rf'\g<1>{new_version}', content)
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated: {file_path}")
                        changed_files += 1
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

print(f"Successfully updated {changed_files} files.")
