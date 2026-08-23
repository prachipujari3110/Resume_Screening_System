import importlib.util
from database import get_connection

packages = [
    ("Flask", "flask"),
    ("Pandas", "pandas"),
    ("NumPy", "numpy"),
    ("Scikit-learn", "sklearn"),
    ("pypdf", "pypdf"),
    ("MySQL Connector", "mysql.connector")
]

print("Checking basic Python packages...")

for name, module in packages:
    if importlib.util.find_spec(module):
        print("[OK]", name)
    else:
        print("[ERROR]", name)

try:
    connection = get_connection()
    connection.close()
    print("[OK] MySQL connection on port 3308")
except Exception as e:
    print("[ERROR] MySQL connection:", e)

print("Setup check completed.")
