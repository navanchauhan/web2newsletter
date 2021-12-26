from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

language = "english"

def summarise(text: str, sentence_count: int = 1, language: str = "english"):
	parser = PlaintextParser.from_string(text,Tokenizer(language))
	stemmer = Stemmer(language)
	summarizer = Summarizer(stemmer)
	summarizer.stop_words = get_stop_words(language)
	return " ".join(str(sentence) for sentence in summarizer(parser.document, sentence_count))