"""
Add test-runner route to app.py
"""

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with @app.route('/analyze'
insert_position = None
for i, line in enumerate(lines):
    if "@app.route('/analyze'" in line:
        insert_position = i
        break

if insert_position is None:
    print("ERROR: Could not find @app.route('/analyze' line")
    exit(1)

# Insert the new route before /analyze
new_route = [
    "\n",
    "@app.route('/test-runner')\n",
    "def test_runner():\n",
    "    \"\"\"Automated indicator test suite\"\"\"\n",
    "    return render_template('test_runner.html')\n",
    "\n",
    "\n"
]

# Insert at position
lines[insert_position:insert_position] = new_route

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Successfully added /test-runner route to app.py")
print(f"   Inserted at line {insert_position}")
print("\n📝 New route:")
print("".join(new_route))