with open('main.py', 'r', encoding='utf-8') as f:
    s = f.read()

old_init = """    def __init__(self, root):
        self._after_ids = {}
        self.root = root
        self.root.title("MikaRoll - Universal Converter")"""

new_init = """    def __init__(self, root):
        ctk.deactivate_automatic_dpi_awareness()
        self._after_ids = {}
        self.root = root
        self.root.withdraw()
        self.root.title("MikaRoll - Universal Converter")"""

if old_init in s:
    s = s.replace(old_init, new_init)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(s)
    print("main.py updated successfully!")
else:
    print("Could not find old_init block.")
