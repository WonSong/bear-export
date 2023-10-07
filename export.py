import sqlite3
import shutil
import os
import re

settings = {
    'bear_base_url': '/Users/won/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/',
    'bear_sqlite_name': 'database.sqlite',
    'assets_folder': 'Local Files/',
    'files_folder': 'Note Files/',
    'images_folder': 'Note Images/',
    'output_folder': '/Users/won/Workspace/NoteArchive/backup/',
    'output_assets_folder': 'assets/'
}


def main():
    bear_notes = retrieve_bear_notes()
    bear_files = retrieve_bear_files()

    if not os.path.exists(settings['output_folder']):
        os.makedirs(settings['output_folder'])
    else:
        shutil.rmtree(settings['output_folder'])
        os.makedirs(settings['output_folder'])

    write_asset_files(bear_files)
    bear_notes = update_notes_with_file_info(bear_notes)
    write_note_files(bear_notes)


def retrieve_bear_notes():
    db_url = f"{settings['bear_base_url']}{settings['bear_sqlite_name']}"
    connection = sqlite3.connect(db_url)
    query = "SELECT notes.Z_PK, notes.ZTITLE, notes.ZTEXT FROM ZSFNOTE AS notes WHERE notes.ZTRASHED = false"
    cursor = connection.cursor()
    cursor.execute(query)
    notes = cursor.fetchall()

    return notes


def retrieve_bear_files():
    db_url = f"{settings['bear_base_url']}{settings['bear_sqlite_name']}"
    connection = sqlite3.connect(db_url)
    query = "SELECT files.ZUNIQUEIDENTIFIER, files.ZNOTE, files.ZFILENAME FROM ZSFNOTEFILE AS files WHERE files.ZNOTE NOT NULL"
    cursor = connection.cursor()
    cursor.execute(query)
    files = cursor.fetchall()

    return files


def write_asset_files(files):
    for file in files:
        file_path = f"{settings['bear_base_url']}{settings['assets_folder']}{settings['images_folder']}{file[0]}/{file[2]}"
        if not os.path.exists(file_path):
            file_path = f"{settings['bear_base_url']}{settings['assets_folder']}{settings['files_folder']}{file[0]}/{file[2]}"
            if not os.path.exists(file_path):
                continue;

        dest = f"{settings['output_folder']}{settings['output_assets_folder']}{file[1]}"

        if not os.path.exists(dest):
            os.makedirs(dest)

        shutil.copyfile(file_path, f"{dest}/{file[2]}")


def update_notes_with_file_info(notes):
    result = []
    pattern = r'(!?\[(?:[^\]]*?)\]\(((?!https?://)[^\)]+?)\))'

    for note in notes:
        note_text = note[2]
        note_id = note[0]

        def replace(match):
            whole_match = match.group(1)
            link_url = match.group(2)
            new_url = f"./assets/{note_id}/{link_url}"

            return whole_match.replace(link_url, new_url)

        note_text = re.sub(pattern, replace, note_text)
        result.append({
            'title': note[1],
            'text': note_text
        })

    return result


def write_note_files(notes):
    for note in notes:
        with open(f"{settings['output_folder']}{note['title']}.md", 'w') as file:
            file.write(note['text'])


if __name__ == "__main__":
    main()
