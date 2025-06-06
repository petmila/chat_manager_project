import string
import emoji

def demojize(text):
    """
    Замена эмоджи на их текстовое описание
    """
    # Убираем знаки препинания и переводим в нижний регистр
    text = ''.join([ch for ch in text if ch not in string.punctuation]).lower()
    # Замена эмоджи на их описание
    text = emoji.demojize(text, language='ru')
    return text
