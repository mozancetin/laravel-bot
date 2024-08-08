import os
import json
import shutil
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from slugify import slugify

def add_to_history(path : str) -> None:
    path = path.replace("\\", "/")
    if not os.path.exists("./history.txt"):
        with open('./history.txt', 'w', encoding="utf-8") as file:
            file.write(path + '\n')
    else:
        with open('./history.txt', 'r+', encoding="utf-8") as file:
            content = file.read()
            file.seek(0, 0)
            file.write(path + '\n' + content)

def check_history() -> None:
    valid_paths = list()
    # Check every line if its a real path or not. If not delete the line from the history.
    with open("./history.txt", "r", encoding="utf-8") as file:
        for line in file:
            path = line.strip()
            if os.path.exists(path):
                if valid_paths.count(path) == 0:
                    valid_paths.append(path)

    # Write the valid paths back to the history file
    with open("./history.txt", "w", encoding="utf-8") as file:
        for path in valid_paths:
            file.write(path.replace("\\", "/") + "\n")

def save_bot_options(path : str, obj : dict) -> None:
    with open(os.path.join(path, "bot_options.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, indent=4))

def get_bot_options(path : str):
    return json.load(open(os.path.join(path, "bot_options.json"), "r", encoding="utf-8"))

def makeCheck(name : str, isChecked : bool, isEnabled : bool = True) -> QtWidgets.QListWidgetItem:
    item = QtWidgets.QListWidgetItem(name)
    if isEnabled:
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
    else:
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsUserCheckable)

    item.setCheckState(QtCore.Qt.Unchecked if isChecked == False else QtCore.Qt.Checked)
    return item

def generate(text : str, snippets : dict) -> str:
    for key, value in snippets.items():
        text = text.replace(key, str(value))
    return text

def read(path : str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def write(text : str, path : str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(cleanup(text))

def slug(text : str) -> str:
    return slugify(text, separator="_")

def tab(text : str, count : int = 1) -> str:
    new_text = ""
    lines = text.split("\n")
    for line in lines:
        if line == "":
            new_text += "\n"
            continue
        
        if line == lines[0]:
            new_text += line + "\n"
            continue

        new_text += "\t" * count + line

        if line != lines[-1]:
            new_text += "\n"

    return new_text

def copy(src : str, dst: str) -> None:
    if os.path.isfile(src):
        shutil.copy(src, dst)
    elif os.path.isdir(src):
        for file in os.listdir(src):
            if os.path.isfile(os.path.join(src, file)):
                shutil.copy(os.path.join(src, file), dst)
            elif os.path.isdir(os.path.join(src, file)):
                if not os.path.isdir(os.path.join(dst, file)):
                    os.mkdir(os.path.join(dst, file))
                copy(os.path.join(src, file), os.path.join(dst, file))

def update_env_variable(path : str, key : str, value):
    if not os.path.exists(path + "/.env"):
        print("Path not exists:", path + "/.env")
        return False
    
    text = ""
    with open(path + "/.env", "r", encoding="utf-8") as f:
        for line in f.readlines():
            if key in line:
                text += key + "=" + ("\n" if str(value) == "" else str(value) + "\n")
            else:
                text += line

    with open(path + "/.env", "w", encoding="utf-8") as f:
        f.write(text)

    return True

def pascalcase(text : str) -> str:
    return slug(text).replace("_", " ").title().replace(" ", "")

def replace_index(text : str, start_index : int, end_index : int, replacement : str) -> str:
    return text[:start_index] + replacement + text[end_index:]

def replace_asset_route(text : str) -> str:
    if ("src" not in text and "href" not in text and "url" not in text) or "http" in text or "mailto" in text or "tel:" in text or "<!--" in text or "#" in text:
        return text
    
    if "src=" in text:
        s = 0
        for _ in range(text.count('src="')):
            start_index = text.find('src="', s) + 5
            end_index = text.find('"', start_index)
            s = end_index + 1
            text_in_between = text[start_index:end_index]
            text = replace_index(text, start_index, end_index, "{{ asset(env('PUBLIC_PATH', '') . '" + text_in_between + "') }}")

    if "url(" in text:
        s = 0
        for _ in range(text.count('url(')):
            start_index = text.find('url(', s) + 4
            end_index = text.find(')', start_index)
            s = end_index + 1
            text_in_between = text[start_index:end_index]
            text = replace_index(text, start_index, end_index, "{{ asset(env('PUBLIC_PATH', '') . '" + text_in_between + "') }}")

    if "href=" in text:
        s = 0
        for _ in range(text.count('href="')):
            if ".html" in text:
                text = text.replace(".html", "", 1)
                start_index = text.find('href="', s) + 6
                end_index = text.find('"', start_index)
                s = end_index + 1
                text_in_between = text[start_index:end_index]
                text = replace_index(text, start_index, end_index, "{{ route('" + text_in_between + "') }}")
            else:
                start_index = text.find('href="', s) + 6
                end_index = text.find('"', start_index)
                s = end_index + 1
                text_in_between = text[start_index:end_index]
                text = replace_index(text, start_index, end_index, "{{ asset(env('PUBLIC_PATH', '') . '" + text_in_between + "') }}")

    return text

def html_to_blade(path : str, start_text : str = "<main>", end_text : str = "</main>", layout : bool = False) -> None:
    with open(path, "r", encoding="utf-8-sig") as f:
        code_lines = f.readlines()

    new_code = ["@extends('layout')\n", "@section('main')\n"]
    new_layout_code = []
    start = False
    for line in code_lines:
        line = replace_asset_route(line)
        if end_text in line:
            start = False
            new_layout_code.append("\t@yield('main')\n")

        if start:
            new_code.append(line)
        else:
            if layout:
                if "</head>" in line:
                    line = "@yield('styles')\n" + line
                elif "</body>" in line:
                    line = "@yield('scripts')\n" + line
                new_layout_code.append(line)

        if start_text in line:
            start = True

    new_code.append("@endsection")

    with open(path, "w", encoding="utf-8-sig") as f:
        f.write("".join(new_code))

    os.rename(path, path.replace(".html", ".blade.php"))

    if layout:
        layout_path = "\\".join(path.replace("\\", "/").split("/")[:-1] + ["layout.blade.php"])
        with open(layout_path, "w", encoding="utf-8-sig") as f:
            f.write("".join(new_layout_code))
        
def html_to_blade_dir(path : str, start_text : str = "<main", end_text : str = "</main>") -> None:
    files = os.listdir(path)
    first = False
    for file in files:
        if not file.endswith(".html"):
            continue

        if not first:
            html_to_blade(os.path.join(path, file), start_text, end_text, True)
            first = True
        else:
            html_to_blade(os.path.join(path, file), start_text, end_text, False)

def clear_spaces(path : str) -> bool:
    if not os.path.exists(path):
        print("Path is not correct: " + path)
        return False
    
    if os.path.isfile(path):
        text = read(path)
        text = text.strip("\n").strip()
        write(text, path)
    elif os.path.isdir(path):
        for item in os.listdir(path):
            clear_spaces(os.path.join(path, item))

    return True

def check_for_html(path : str):
    if not os.path.exists(path):
        print("Path doesn't exists: " + path)
        return None

    return any(list(map(lambda file: file.endswith(".html"), os.listdir(path))))

def cleanup(text : str) -> str:
	temp = ""
	last = False
	for line in text.split("\n"):
		if line == text.split("\n")[-1]:
			last = True
		if line.replace("\t", "").strip() == "":
			line = ""
		temp += line + ("\n" if last else "")

	temp = temp.replace("\n\n\n", "\n")
	return temp