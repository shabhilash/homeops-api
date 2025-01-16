import os

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        if '.venv' in root:
            continue
        if '.git' in root:
            continue
        if 'pytest_cache' in root:
            continue
        if '.idea' in root:
            continue
        if '__pycache__' in root:
            continue
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}{f}')

list_files(os.path.dirname(os.getcwd()))
