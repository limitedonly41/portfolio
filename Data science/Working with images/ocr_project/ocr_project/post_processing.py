import re, csv
from collections import Counter


def words(text): return re.findall(r'\w+', text.lower())


WORDS = Counter(words(open('words_alpha.txt').read()))


def P(word, N=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / N


def correction(word):
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)


def decode(word):
    letters_map = {'@': 'a', '$': 's', '!': 'i', '1': 'l', '0': 'o', '(': 'c', '+': 't'}
    symbol_chars = 0
    word = list(word.lower())
    for i in range(len(word)):
        if word[i] in letters_map:
            word[i] = letters_map.get(word[i])
            symbol_chars += 1
    return ''.join(word), symbol_chars


def deleteDuplicates(word):
    dups_dictionary = {word: 0}
    splits = [(word[:i], word[i:]) for i in range(1, len(word))]
    deletes = [L + R[1:] for L, R in splits if L[-1] == R[0]]
    if len(deletes) > 0:
        repeated_chars = 1
        dups_dictionary[deletes[0]] = repeated_chars
        # Try to remove any other duplicates like removing other o's in shooow
        while len(deletes) > 1:
            word = list(set(deletes))[0]
            splits = [(word[:i], word[i:]) for i in range(1, len(word))]
            deletes = [L + R[1:] for L, R in splits if L[-1] == R[0]]
            repeated_chars += 1
            dups_dictionary[deletes[0]] = repeated_chars
        return dups_dictionary
    return None


def transpose(word):
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    return transposes


def candidates(word):
    "Generate possible spelling corrections for word."
    return known([word]) or known(edits1(word)) or known(edits2(word)) or [word]


def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)


def edits1(word):
    "All edits that are one edit away from `word`."
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def correct_text(text):
    if len(text.split(' ')) > 1:
        print('Start of words in "{}"'.format(text))
        for w in text.split(' '):
            print('***', end='')
            correct_word(w)
        print('End of words in "{}"'.format(text))
    else:
        correct_word(text)


def correct_word(word):
    original_word = word.lower()
    correction_dictionary = {'Original_word': original_word, 'correction': '',
                             'symbol_chars': 0, 'repeated_chars': 0, 'swap_chars': 0, 'OOV': 0}

    # Search if the input is exist in the dictionary
    if original_word in WORDS:
        correction_dictionary['correction'] = original_word
        return correction_dictionary

    # Check if the input is a number
    if original_word.isdigit():
        correction_dictionary['correction'] = original_word
        return correction_dictionary
    else:
        word = original_word

    # Search for symbols, decode them and try correction on decoded word
    decoded_word, symbols_count = decode(word)
    if symbols_count > 0:
        # Try correction after decode
        correction_dictionary['symbol_chars'] += symbols_count
        if correction(decoded_word) == decoded_word and decoded_word in WORDS:
            # correction_dictionary['symbol_chars'] += symbols_count
            correction_dictionary['correction'] = decoded_word
            return correction_dictionary
        # If we still didn't get a match after decode,
        # then we will use the decoded word for more analysis
        else:
            word = decoded_word

    # Try deleteDuplicates
    if deleteDuplicates(word):
        duplicates_dictionary = deleteDuplicates(word)
        for trimmed_word in duplicates_dictionary:
            if correction(trimmed_word) == trimmed_word and trimmed_word in WORDS:
                correction_dictionary['repeated_chars'] += duplicates_dictionary.get(trimmed_word)
                correction_dictionary['correction'] = trimmed_word
                # print('Input word is: {}, possible match is: {}, {}' \
                #   .format(original_word, trimmed_word, correction_dictionary))
                return correction_dictionary
        # If we still didn't get a match after deleteDuplicates,
        # then we will use the deleteDuplicates word for more analysis
        # if there are trimmed duplicates
        if duplicates_dictionary.get(trimmed_word) > 0:
            correction_dictionary['repeated_chars'] += duplicates_dictionary.get(trimmed_word)
            word = trimmed_word

    # Try transpose

    transposes = transpose(word)
    for transposed_word in transposes:
        if correction(transposed_word) == transposed_word and transposed_word in WORDS:
            correction_dictionary['swap_chars'] += 1
            correction_dictionary['correction'] = transposed_word
            # print('Input word is: {}, possible match is: {}, {}' \
            #   .format(original_word, transposed_word, correction_dictionary))
            return correction_dictionary

    # Otherwise, we will match the exact input word
    # or the suggested correction of input word
    # if it exists in the wordlist
    if original_word in WORDS:
        correction_dictionary['correction'] = original_word
        return correction_dictionary

    if correction(original_word) in WORDS:
        correction_dictionary['correction'] = correction(original_word)
        correction_dictionary['symbol_chars'] = 0
        correction_dictionary['repeated_chars'] = 0
        correction_dictionary['swap_chars'] = 0
        correction_dictionary['OOV'] += 1

        return correction_dictionary


def post_process(input):
    with open(input, 'r') as word_list:
        words = word_list.read().split('\n')

    n_words = []
    for word in words:
        n_words.append(word + ' \n')

    processed_words = []
    for word in n_words:
        processed_words.extend(
            word.replace('\x0c', '').replace('(', '').replace('.', ' .').replace(')', '').replace('^', '').split(' '))

    corrected_words = []

    for i in processed_words:
        try:
            if i == '':
                continue
            if i == '\n':
                corrected_words.append('\n')
                continue
            if i == '.':
                corrected_words.append('.')
                continue
            if i.isupper():
                corrected_words.append(correct_word(i)['correction'].upper())
                continue
            if not i.islower():
                corrected_words.append(correct_word(i)['correction'].capitalize())
                continue
            corrected_words.append(correct_word(i)['correction'])
        except:
            corrected_words.append(i)

    with open('post_processed.txt', 'w') as f:
        for item in corrected_words:
            if item == '.':
                f.write(item)
            else:
                f.write(' ' + item)