import sqlite3
import shutil
import os
import re
import json
from datetime import datetime, timedelta

# Load settings from config file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
with open(config_path, 'r') as f:
    settings = json.load(f)

# Expand user paths
settings['bear_base_url'] = os.path.expanduser(settings['bear_base_url'])
settings['output_folder'] = os.path.expanduser(settings['output_folder'])


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
    query = "SELECT notes.Z_PK, notes.ZTITLE, notes.ZTEXT, notes.ZCREATIONDATE, notes.ZMODIFICATIONDATE FROM ZSFNOTE AS notes WHERE notes.ZTRASHED = false"
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


def extract_tags(note_text):
    """Extract tags from note text. Tags start with # and can be nested with /."""
    # Require whitespace or start of line before #, exclude URL anchors
    tag_pattern = r'(?:^|(?<=\s))#([a-zA-Z0-9_]+(?:/[a-zA-Z0-9_]+)*)(?=\s|$)'
    tags = re.findall(tag_pattern, note_text, re.MULTILINE)
    return tags


def convert_core_data_timestamp(timestamp):
    """Convert Core Data timestamp to datetime. Core Data uses 2001-01-01 as reference."""
    if timestamp is None:
        return None
    reference_date = datetime(2001, 1, 1)
    return reference_date + timedelta(seconds=timestamp)


def update_notes_with_file_info(notes):
    result = []
    pattern = r'(!?\[(?:[^\]]*?)\]\(((?!https?://)[^\)]+?)\))'

    for note in notes:
        note_text = note[2]
        note_id = note[0]
        created_timestamp = note[3]
        modified_timestamp = note[4]

        def replace(match):
            whole_match = match.group(1)
            link_url = match.group(2)
            new_url = f"./assets/{note_id}/{link_url}"

            return whole_match.replace(link_url, new_url)

        note_text = re.sub(pattern, replace, note_text)
        tags = extract_tags(note_text)
        
        result.append({
            'title': note[1],
            'text': note_text,
            'tags': tags,
            'created': convert_core_data_timestamp(created_timestamp),
            'modified': convert_core_data_timestamp(modified_timestamp)
        })

    return result


def write_note_files(notes):
    for note in notes:
        tags = note.get('tags', [])
        
        # Build metadata section
        metadata_lines = []
        if note.get('created'):
            metadata_lines.append(f"Created: {note['created'].strftime('%Y-%m-%d %H:%M:%S')}")
        if note.get('modified'):
            metadata_lines.append(f"Modified: {note['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        metadata = '\n'.join(metadata_lines)
        
        # Prepend metadata to note content
        content = note['text']
        if metadata:
            content = f"{metadata}\n\n---\n\n{content}"
        
        if not tags:
            # If no tags, write to root folder
            file_path = f"{settings['output_folder']}{note['title']}.md"
            with open(file_path, 'w') as file:
                file.write(content)
        else:
            # Write note to each tag folder
            for tag in tags:
                tag_folder = os.path.join(settings['output_folder'], tag)
                os.makedirs(tag_folder, exist_ok=True)
                
                file_path = os.path.join(tag_folder, f"{note['title']}.md")
                with open(file_path, 'w') as file:
                    file.write(content)


if __name__ == "__main__":
    main()
