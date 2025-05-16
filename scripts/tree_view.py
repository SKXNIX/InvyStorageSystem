import os


def print_tree(startpath, ignore_dirs=None, prefix=""):
    """Рекурсивная функция для печати дерева директорий с игнорированием указанных директорий."""
    if ignore_dirs is None:
        ignore_dirs = []
    
    try:
        entries = os.listdir(startpath)
    except PermissionError:
        print(prefix + "└── [Permission Denied]")
        return
    
    entries.sort(key=lambda x: (not os.path.isdir(os.path.join(startpath, x)), x))
    
    for i, entry in enumerate(entries):
        path = os.path.join(startpath, entry)
        is_last = i == len(entries) - 1
        marker = "└── " if is_last else "├── "
        
        if os.path.isdir(path) and entry in ignore_dirs:
            print(prefix + marker + f"{entry}/")
        else:
            print(prefix + marker + entry)
            
            if os.path.isdir(path) and entry not in ignore_dirs:
                new_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(path, ignore_dirs, new_prefix)


start_directory = '.'  # Начальная директория
ignore_directories = ['css', 'fonts', 'img', 'js', '.vs', '.git', '__pycache__', 'migrations']  # Список директорий для игнорирования
print_tree(start_directory, ignore_directories)