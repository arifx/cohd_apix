#get cooccurrence matrix
from __future__ import division
from collections import Counter, defaultdict
import os
from random import shuffle

words = None
word_to_id = None
cooccurrence_matrix = None
embeddings = None


def _window(region, start_index, end_index):
    """
    Returns the list of words starting from `start_index`, going to `end_index`
    taken from region. If `start_index` is a negative number, or if `end_index`
    is greater than the index of the last word in region, this function will pad
    its return value with `NULL_WORD`.
    """
    last_index = len(region) + 1
    selected_tokens = region[max(start_index, 0):min(end_index, last_index) + 1]
    return selected_tokens


def _context_windows(region, left_size, right_size):
    for i, word in enumerate(region):
        start_index = i - left_size
        end_index = i + right_size
        left_context = _window(region, start_index, i - 1)
        right_context = _window(region, i + 1, end_index)
        yield (left_context, word, right_context)


def _fit_to_corpus(corpus, vocab_size, min_occurrences, left_size, right_size):
        word_counts = Counter()
        cooccurrence_counts = defaultdict(float)
        for region in corpus:
            word_counts.update(region)
            #for l_context, word, r_context in _context_windows(region, left_size, right_size):
            for l_context, word, r_context in _context_windows("123 ab 123 cd", 1, 1):
                for i, context_word in enumerate(l_context[::-1]):
                    # add (1 / distance from focal word) for this pair
                    cooccurrence_counts[(word, context_word)] += 1 / (i + 1)
                for i, context_word in enumerate(r_context):
                    cooccurrence_counts[(word, context_word)] += 1 / (i + 1)
        if len(cooccurrence_counts) == 0:
            raise ValueError("No coccurrences in corpus. Did you try to reuse a generator?")
        words = [word for word, count in word_counts.most_common(vocab_size)
                        if count >= min_occurrences]
        word_to_id = {word: i for i, word in enumerate(words)}
        cooccurrence_matrix = {
            (word_to_id[words[0]], word_to_id[words[1]]): count
            for words, count in cooccurrence_counts.items()
            if words[0] in word_to_id and words[1] in word_to_id}


_fit_to_corpus("aa bb cc",3, 1,1,1)
