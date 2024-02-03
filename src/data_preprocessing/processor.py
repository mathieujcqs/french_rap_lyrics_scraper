import pandas as pd
from collections import Counter
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS

from src.paths import DATA_DIR
from src.utils.logger import get_console_logger
from src.utils.file_utils import read_songs_json_files



logger = get_console_logger()

def add_int_data(df):
    df['nb_characters'] = df.lyrics.apply(lambda x: len(x) if pd.notnull(x) else 0)
    df['nb_words'] = df.lyrics.apply(lambda x: len(x.strip().split()) if pd.notnull(x) else 0)
    return df

def clean_lyrics(df):
    nlp = spacy.load("fr_core_news_sm")

    df["clean_str"] = df["lyrics"].apply(lambda x: " ".join([word for word in x.lower().strip().split() if word not in STOP_WORDS]))
    df['lemma_str'] = df['clean_str'].apply(lambda x: " ".join([word.lemma_ for word in nlp(x)]))

    return df

def add_most_common_words(df):

    df["most_frequent_words_top_5"] = df['clean_str'].apply(lambda x: [word for word, _ in Counter(x.strip().split()).most_common(5)])
    df["most_frequent_word"] = df['most_frequent_words_top_5'].apply(lambda x: x[0])

    return df


def get_word_emotion(emotion_dict, word):
    return [emotion for emotion, present in emotion_dict.get(word, {}).items() if present]

def analyze_lyrics(lyrics, emotion_dict):
    words = lyrics.lower().strip().split()
    emotions = [emotion for word in words for emotion in get_word_emotion(emotion_dict, word)]

    return emotions

def get_most_frequent_sentiment(lyrics, emotion_dict):

    emotions = analyze_lyrics(lyrics, emotion_dict)

    if emotions:
        emotions_counts = Counter(emotions)
        return emotions_counts.most_common(1)[0][0]
    else:
        return 'neutre'

def main():
    songs_data = read_songs_json_files(f"{DATA_DIR}/raw")

    df = pd.DataFrame(songs_data)
    logger.info('Songs data loaded in a Dataframe')

    # change lyrics columns to string to ensure good processing
    df['lyrics'] = df['lyrics'].astype("string")

    logger.info('Data enrichment process')
    df = add_int_data(df)
    # data selection to avoid outliers and songs with no lyrics
    df = df.loc[(df.nb_words <= 1000) & (df.nb_words >= 300)]
    logger.info('Added words and characters counts')
    
    df = clean_lyrics(df)
    logger.info('Cleaned raw lyrics text (stop words removal and lemmatization)')
    
    df = add_most_common_words(df)
    logger.info('Added most common words')

    lexicon_df = pd.read_csv(DATA_DIR / 'extrernal/FEEL.csv', delimiter=';')

    lexicon_df = lexicon_df.drop_duplicates(subset='word')
    emotion_dict = lexicon_df.set_index('word')[['joie', 'peur', 'tristesse', 'colère', 'surprise', 'dégout']].to_dict()

    df['main_sentiment'] = df["lemma_str"].apply(lambda x: get_most_frequent_sentiment(x, emotion_dict))
    logger.info('Added most common sentiment')

    df.to_parquet(DATA_DIR / 'intermediate/lyrics_data.parquet')

if __name__ == '__main__':
    main()