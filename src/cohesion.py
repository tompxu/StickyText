import math
import nltk
import numpy
import itertools
import nlputil
from docstructure import *

# return a list of sentence pairs
# usage: for x,y = sentence_pair(..): ...
def sentence_pairs(doc, is_local):
    if is_local:
        return [(doc.sents[i], doc.sents[i+1]) 
            for i in range(0, len(doc.sents)-2)]
    else:
        return [(doc.sents[i], doc.sents[j])
            for i, j in itertools.combinations(range(len(doc.sents)), 2)]


# measuring word overlapping a pair of sentences
# words_type should be a function gotten from words_typed()
def jaccard_index(sent1, sent2, word_type):
    word_set = lambda x: set([y.text for y in word_type(x)])
    set1 = word_set(sent1)
    set2 = word_set(sent2)
    if len(set1)==0 and len(set2)==0:
        return 0.0
    else:
        return len(set1.intersection(set2)) / float(len(set1.union(set2)))

# measuring document cohesion based on word overlapping (jaccard index)
def word_overlap_cohesion(doc, is_local, word_type):
    if len(doc.sents) < 2: return 0
    return numpy.mean(
        [jaccard_index(x, y, word_type)
        for x, y in sentence_pairs(doc, is_local)])

# return a frequency distribution dictionary of words
def word_frequency(words):
    return nltk.FreqDist([x.text for x in words])

# return the cosine between two vectors, stored as dictionary objects
def cosine_vectors(vector1, vector2):
    prod = 0.0
    v1_sq = 0.0
    v2_sq = 0.0
    for x in vector1:
        y = vector1[x]
        v1_sq += y * y
        if x in vector2:
            prod += y * vector2[x]
    for x in vector2:
        y = vector2[x]
        v2_sq += y * y
    if v1_sq == 0 or v2_sq == 0:
        return 0
    else:
        return prod / math.sqrt(v1_sq * v2_sq)

# measuring word frequency distribution similarity between a pair of sentences
def cosine_similarity(sent1, sent2, word_type):
    vector1 = word_frequency(word_type(sent1))
    vector2 = word_frequency(word_type(sent2))
    return cosine_vectors(vector1, vector2)

# meausring document cohesion
def word_dist_cohesion(doc, is_local, word_type):
    if len(doc.sents) < 2: return 0
    return numpy.mean(
        [cosine_similarity(x, y, word_type)
        for x, y in sentence_pairs(doc, is_local)])

# measuring max_max_similarity between any sense combination between any word pair of a pair of sentences
# By default: word_type = lambda x: x.nouns
# Simtype should be nlputil.select_path_similarity() or alike, see nlputil.py for more options
def max_max_similarity(sent1, sent2, word_type, simtype):
    words1 = word_type(sent1)
    words2 = word_type(sent2)
    if len(words1)==0 or len(words2)==0:
        return 0
    else:
        return max([nlputil.max_similarity(x, y, simtype) 
            for x in words1 for y in words2])

# measuring WordNet-based cohesion using max_max_similarity
# caution: extremely slow
def wordnet_cohesion(doc, is_local=True, word_type=lambda x: x.nouns, simtype=nlputil.select_resnick_similarity()):
    if len(doc.sents) < 2: return 0
    if not doc.pos_tagged:
        doc.pos_tag()
    return numpy.mean(
        [max_max_similarity(x, y, word_type, simtype)
        for x, y in sentence_pairs(doc, is_local)])
