import os
import shutil

def copy_files_recursive(source_dir, dest_dir):
    if os.path.exists(dest_dir):
        print(f"Deleting existing directory: {dest_dir}")
        shutil.rmtree(dest_dir)

    print(f"Creating directory: {dest_dir}")
    os.mkdir(dest_dir)

    _copy_contents(source_dir, dest_dir)

def _copy_contents(source_dir, dest_dir):
    items = os.listdir(source_dir)

    for item in items:
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)

        if os.path.isfile(source_path):
            print(f"Copying file: {source_path} -> {dest_path}")
            shutil.copy(source_path, dest_path)
        else:
            print(f"Creating directory: {dest_path}")
            os.mkdir(dest_path)
            _copy_contents(source_path, dest_path)
