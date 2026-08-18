import os
import ast
import sys

stdlib = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else set()
stdlib.update({'os', 'sys', 're', 'threading', 'json', 'tempfile', 'shutil', 'traceback', 'tkinter', 'subprocess'})

found_imports = set()

for root, dirs, files in os.walk('.'):
    if '.conda' in root or '__pycache__' in root or 'build' in root or 'dist' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                found_imports.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                found_imports.add(node.module.split('.')[0])
                except Exception as e:
                    pass

third_party = found_imports - stdlib

local_modules = {'engines', 'utils', 'qmc_decrypt'}
third_party = third_party - local_modules

print("Found third-party imports:", sorted(list(third_party)))
