import string
import emoji
import nltk
from nltk import SnowballStemmer, word_tokenize
from nltk.corpus import stopwords


def preprocess(text):
    """
    Проводит лемматизацию, удаляет знаки препинания, стоп-слова
    """
    # nltk.download('stopwords')
    # nltk.download('punkt_tab')

    # Убираем знаки препинания и переводим в нижний регистр
    text = ''.join([ch for ch in text if ch not in string.punctuation]).lower()

    # Замена эмоджи на их описание
    text = emoji.demojize(text, language='ru')
    text = ' '.join(text.split(':'))

    # # Убираем стоп-слова
    # tokens = word_tokenize(text)
    # stop_words = set(stopwords.words('russian'))
    # filtered_tokens = [word for word in tokens if word not in stop_words]
    #
    # # Приводим слова к начальной форме/корню
    # stemmer = SnowballStemmer("russian")
    # lemmatized_words = [stemmer.stem(word) for word in filtered_tokens]

    return text
