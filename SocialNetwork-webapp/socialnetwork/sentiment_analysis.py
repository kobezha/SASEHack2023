import nltk
nltk.download([
    "vader_lexicon","punkt",
])
from nltk.sentiment.vader import SentimentIntensityAnalyzer


# given text, return if positive , negative or neutral sentiment
# 1 = positive
# -1 = negative
# 0 = neutral
def get_sentiment(text):
    
    # VADER( Valence Aware Dictionary for Sentiment Reasoning)
    # NLTK module that provides sentiment scores based on the words used.
    sia = SentimentIntensityAnalyzer()
    polarity_scores = sia.polarity_scores(text)

    # compound score is the overall sentiment score
    # ranges from -1 (extremely negative) to 1 (extremely positive)
    compound_score = polarity_scores['compound']

    return compound_score

    if (compound_score >= 0): return 1
    elif (compound_score < 0): return -1
    return 0


def main():
    print(get_sentiment("I'm not feeling really good today."))
    print(get_sentiment("It's a bit disappointing to see how little people care about me"))

if __name__ == "__main__":
    main()
