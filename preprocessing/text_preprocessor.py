import re
import nltk
from bs4 import BeautifulSoup

# Ensure necessary NLTK data packages are downloaded automatically
def _init_nltk():
    for pkg in ['stopwords', 'punkt', 'punkt_tab']:
        try:
            nltk.data.find(f'tokenizers/{pkg}' if pkg in ['punkt', 'punkt_tab'] else f'corpora/{pkg}')
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception as e:
                print(f"Warning: Could not download NLTK package '{pkg}': {e}")

_init_nltk()

class TextPreprocessor:
    """
    Preprocessing pipeline matching university thesis model training:
    Email Subject + Body
    -> Lowercase
    -> Remove HTML
    -> Remove URLs
    -> Remove Email Addresses
    -> Remove Special Characters
    -> Normalize Whitespace
    -> Remove English Stopwords
    -> Tokenization
    """

    def __init__(self):
        try:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            # Fallback english stopwords if NLTK stopwords failed to load
            self.stop_words = {
                'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't",
                'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't",
                'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down',
                'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't",
                'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself',
                'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it',
                "it's", 'its', 'itself', 'let\'s', 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not',
                'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over',
                'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such',
                'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's",
                'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too',
                'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were',
                "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's",
                'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're",
                "you've", 'your', 'yours', 'yourself', 'yourselves'
            }

    def clean_html(self, text: str) -> str:
        """Remove HTML tags using BeautifulSoup with regex fallback."""
        if not text or '<' not in text:
            return text or ""
        try:
            soup = BeautifulSoup(text, "html.parser")
            return soup.get_text(separator=' ')
        except Exception:
            return re.sub(r'<[^>]+>', ' ', text)

    def remove_urls(self, text: str) -> str:
        """Remove URLs starting with http, https, or www."""
        return re.sub(r'https?://\S+|www\.\S+', ' ', text)

    def remove_email_addresses(self, text: str) -> str:
        """Remove email addresses."""
        return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', ' ', text)

    def remove_special_characters(self, text: str) -> str:
        """Remove non-alphanumeric characters, leaving space."""
        return re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    def tokenize(self, text: str) -> list[str]:
        """Tokenize text into words using NLTK word_tokenize with fallback."""
        try:
            return nltk.word_tokenize(text)
        except Exception:
            return re.findall(r'\b\w+\b', text)

    def preprocess(self, text: str) -> str:
        """
        Execute full preprocessing sequence:
        Subject + Body -> Lowercase -> Remove HTML -> Remove URLs -> Remove emails
        -> Remove special chars -> Normalize whitespace -> Remove Stopwords -> Tokenization -> String output
        """
        if not text:
            return ""

        # Step 1: Lowercase
        text = text.lower()

        # Step 2: Remove HTML
        text = self.clean_html(text)

        # Step 3: Remove URLs
        text = self.remove_urls(text)

        # Step 4: Remove email addresses
        text = self.remove_email_addresses(text)

        # Step 5: Remove special characters
        text = self.remove_special_characters(text)

        # Step 6: Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Step 7: Tokenization
        tokens = self.tokenize(text)

        # Step 8: Remove English Stopwords
        filtered_tokens = [w for w in tokens if w not in self.stop_words and len(w) > 1]

        # Re-combine into processed text string suitable for TF-IDF vectorizer.transform()
        return ' '.join(filtered_tokens)


_preprocessor_instance = TextPreprocessor()

def preprocess_email_text(text: str) -> str:
    """Convenience functional interface for preprocessing email text."""
    return _preprocessor_instance.preprocess(text)
