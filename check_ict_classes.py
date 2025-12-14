# check_ict_classes.py
"""Check actual class names in ICT modules"""

import os
import re

ict_dir = r"C:\Users\Gebruiker\Edgelab\core\strategy_modules\ict"

print("Checking ICT module class names...")
print("=" * 60)

if os.path.exists(ict_dir):
    files = sorted([f for f in os.listdir(ict_dir) if f.endswith('.py') and f != '__init__.py'])
    
    for file in files:
        filepath = os.path.join(ict_dir, file)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find class definitions
                classes = re.findall(r'^class (\w+)', content, re.MULTILINE)
                if classes:
                    print(f"{file:<30} -> {classes[0]}")
        except Exception as e:
            print(f"{file:<30} -> Error: {e}")
else:
    print(f"Directory not found: {ict_dir}")

print("=" * 60)