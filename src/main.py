import sys

from copystatic import copy_files_recursive
from generate_page import generate_page_recursive

dir_path_static = "./static"
dir_path_public = "./public"
dir_path_content = "./content"
template_path = "./template.html"

def main():
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]

    copy_files_recursive(dir_path_static, dir_path_public)

    generate_page_recursive(dir_path_content, template_path, dir_path_public, basepath)

if __name__ == "__main__":
    main()
