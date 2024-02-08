import pandas as pd

from src.paths import DATA_DIR
from src.utils.logger import get_console_logger
from src.utils.file_utils import read_songs_json_files, get_config
from utils.metadata_utils import add_int_data, clean_lyrics, add_most_common_words, get_most_frequent_emotion

logger = get_console_logger()

def main():
    """
    Main script to enrich song lyrics with metadata and preprocess text for analysis.
    
    The script performs the following operations:
    - Loads song data from JSON files.
    - Enriches the data with metadata such as character counts, the main emotion of the song,
      and the most common words.
    - Cleans the lyrics by removing stop words and applying lemmatization to generate a
      "clean" version of the lyrics for further analysis.
    - Saves the enriched and cleaned data to a Parquet file for efficient storage and access.
    
    Configuration for the script, including file paths and processing parameters, 
    is loaded from a 'main.yml' file.
    
    Returns:
        None
    """
    
    CONFIG = get_config("main.yml")
    char_upperbound  = CONFIG["preprocessor"]["lyrics_char_upperbound"]
    char_lowerbound  = CONFIG["preprocessor"]["lyrics_char_lowerbound"]
    emotion_csv_path = CONFIG["preprocessor"]["emotions_csv_path"]
    save_path        = CONFIG["preprocessor"]["save_path"]
    emotions         = CONFIG["preprocessor"]["emotions"]
    
    songs_data = read_songs_json_files(f"{DATA_DIR}/raw")

    df = pd.DataFrame(songs_data)
    logger.info('Songs data loaded in a Dataframe')

    # change lyrics columns to string to ensure good processing
    df['lyrics'] = df['lyrics'].astype("string")

    logger.info('Data enrichment process')
    df = add_int_data(df)
    # data selection to avoid outliers and songs with no/ to much lyrics
    df = df.loc[(df.nb_words <= char_upperbound) & (df.nb_words >= char_lowerbound)]
    logger.info('Added words and characters counts')
    
    df = clean_lyrics(df)
    logger.info('Cleaned raw lyrics text (stop words removal and lemmatization)')
    
    df = add_most_common_words(df)
    logger.info('Added most common words')

    lexicon_df = pd.read_csv(DATA_DIR / emotion_csv_path, delimiter=';')

    lexicon_df = lexicon_df.drop_duplicates(subset='word')
    emotion_dict = lexicon_df.set_index('word')[emotions].to_dict()

    df['main_sentiment'] = df["lemma_str"].apply(lambda x: get_most_frequent_emotion(x, emotion_dict))
    logger.info('Added most common sentiment')

    df.to_parquet(DATA_DIR / save_path)

if __name__ == '__main__':
    main()