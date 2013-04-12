import sys
import nlputil
from listtool import catlist
from hyphen import Hyphenator
import nltk
# Library references:
# PyHyphen: https://pypi.python.org/pypi/PyHyphen/2.0.2
# NLTK: http://nltk.googlecode.com/svn/trunk/doc/book/book.html
# NLTK-Tagger: https://nltk.googlecode.com/svn/trunk/doc/howto/tag.html

class Word:
    h_en = Hyphenator('en_US')
    def __init__(self, text):
        self.text = text
    def __str__(self):
        return self.text
    def numsyl(self):
        return max(1, len(Word.h_en.syllables(unicode(self.text))))

class Sentence:
    def __init__(self, text):
        self.text = text
        self.words = [Word(x) for x in nltk.word_tokenize(text) if x]
        # pwords: tokens excluding any punctuation tokens
        self.pwords = nlputil.remove_punctuation_from_words(self.words)
        # cwords: content words, exclusing any stopwords
        self.cwords = nlputil.remove_stopwords(self.pwords)
        # scwords: stemmed lower-cased content words
        self.scwords = [Word(x) for x in nlputil.stem_lower_words(self.cwords)]
    def __str__(self):
        return self.text
    def pos_tag(self):
        tags = nltk.pos_tag([x.text for x in self.words])
        self.nouns = [x for x, y in tags if y in ('NN','NNP', 'NNS')]

class Paragraph:
    sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
    def __init__(self, text):
        self.text = text.strip()
        self.sents = [Sentence(x) for x in Paragraph.sent_tokenizer.tokenize(text) if x]
        self.pwords = catlist([x.pwords for x in self.sents])
        self.cwords = catlist([x.cwords for x in self.sents])
        self.scwords = catlist([x.scwords for x in self.sents])
    def __str__(self):
        return self.text
    def pos_tag(self):
        for x in self.sents:
            x.pos_tag()
        self.nouns = catlist([x.nouns for x in self.sents])

class Document:
    def __init__(self, text):
        self.text = text.strip()
        tmppars = [x for x in text.split('\n') if x]
        self.pars = [Paragraph(x) for x in tmppars]
        self.sents = catlist([x.sents for x in self.pars])
        self.pwords = catlist([x.pwords for x in self.pars])
        self.cwords = catlist([x.cwords for x in self.pars])
        self.scwords = catlist([x.scwords for x in self.pars])
        self.pos_tagged = False
    def __str__(self):
        return self.text
    # tags all words iteratively in the document, create noun word lists in sentences
    # The tagging process is very slow.
    def pos_tag(self):
        for x in self.pars:
            x.pos_tag()
        self.pos_tagged = True

# return a function that retrieves the word list of the desired type from a sentence
# stem overrides remove_stopwords, which means stem always removes stopwords
def words_typed(stem, remove_stopwords):
    if stem:
        return lambda x: x.scwords
    elif remove_stopwords:
        return lambda x: x.cwords
    else:
        return lambda x: x.pwords
