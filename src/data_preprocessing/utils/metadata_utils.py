import pandas as pd
from collections import Counter

import spacy
from spacy.lang.fr.stop_words import STOP_WORDS


def add_int_data(df):
    """Adds metadata with int types such as nb_char and nb_words.

    Args:
    df (pandas dataframe): the base dataframe.

    Returns:
    Pandas Dataframe: df with the added columns.
    """
    
    df['nb_characters'] = df.lyrics.apply(lambda x: len(x) if pd.notnull(x) else 0)
    df['nb_words'] = df.lyrics.apply(lambda x: len(x.strip().split()) if pd.notnull(x) else 0)
    return df
  
def clean_lyrics(df):
    """Cleans the song lyrics by removing the stop words and lemmatize the lyrics and adds one column for each action.

    Args:
    df (pandas dataframe): the base dataframe.

    Returns:
    Pandas Dataframe: df with the added columns.
    """

    nlp = spacy.load("fr_core_news_sm")

    df["clean_str"] = df["lyrics"].apply(lambda x: " ".join([word for word in x.lower().strip().split() if word not in STOP_WORDS]))
    df['lemma_str'] = df['clean_str'].apply(lambda x: " ".join([word.lemma_ for word in nlp(x)]))

    return df

def add_most_common_words(df):
    """Adds a new column containing the 5 most common words in the lyrics.

    Args:
    df (pandas dataframe): the base dataframe.

    Returns:
    Pandas Dataframe: df with the added column.
    """
    
    df["most_frequent_words_top_5"] = df['clean_str'].apply(lambda x: [word for word, _ in Counter(x.strip().split()).most_common(5)])
    df["most_frequent_word"] = df['most_frequent_words_top_5'].apply(lambda x: x[0])

    return df

def get_word_emotion(emotion_dict, word):
    """Returns the emotion of a word.

    Args:
    emotion_dict (dict): a dict containing the word as key and an emotion as value.
    word (str): the word we want the emotion from

    Returns:
    Pandas Dataframe: df with the added column.
    """
    return [emotion for emotion, present in emotion_dict.get(word, {}).items() if present]

def analyze_lyrics_emotion(lyrics, emotion_dict):
    """Returns a list of emotions related to the lyrics words.

    Args:
    lyrics (str): the lyrics we want to analyze the emotion from
    emotion_dict (dict): a dict containing the word as key and an emotion as value.
    
    Returns:
    List: list of emotions.
    """
    words = lyrics.lower().strip().split()
    emotions = [emotion for word in words for emotion in get_word_emotion(emotion_dict, word)]

    return emotions

def get_most_frequent_emotion(lyrics, emotion_dict):
    """Returns the most frequent emotion of the lyrics.

    Args:
    lyrics (str): the lyrics we want to analyze the emotion from
    emotion_dict (dict): a dict containing the word as key and an emotion as value.
    
    Returns:
    Str: A string containing the most freauent emotion of the lyrics.
    """
    emotions = analyze_lyrics_emotion(lyrics, emotion_dict)

    if emotions:
        emotions_counts = Counter(emotions)
        return emotions_counts.most_common(1)[0][0]
    else:
        return 'neutre'