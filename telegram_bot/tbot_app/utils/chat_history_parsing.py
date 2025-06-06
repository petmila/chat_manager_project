import json
import pathlib


def parse_chat_history(downloaded_file: bytes, file_path, source_chat_id, chat_title):
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    with open(file_path, encoding="utf-8") as f:
        d = json.load(f)
        for message in d['messages']:
            if message['type'] == 'message':
                text = message['text']
                if isinstance(text, list):
                    text = ''.join([t if isinstance(t, str) else t['text'] for t in text])
                data = {'text': text, 'timestamp': message['date'],
                        'employee_account': {
                            'nickname': message['from'],
                            'source': 'Telegram'},
                        'chat': {
                            'source_chat_id': source_chat_id,
                            'chat_source': 'Telegram',
                            'name': chat_title,
                        }}
                yield data
    file_to_rem = pathlib.Path(file_path)
    file_to_rem.unlink()


