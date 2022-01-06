import heapq
import random
import re
import statistics
import string

from collections import defaultdict

DEBUG = False
WORD_LENGTH = 5
# WORD_FILE = '/usr/share/dict/words'
WORD_FILE = 'five_letter_words.txt'

five_letter_regex = re.compile(r'^[A-Z]{5}$')  # Only match lower-case words
five_letter_words = []
with open(WORD_FILE, 'r') as dictionary:
    for word in dictionary:
        if five_letter_regex.match(word):
            five_letter_words.append(word.strip())


def determine_starting_words(words):
    letter_frequences = defaultdict(int)
    for word in words:
        for letter in word:
            letter_frequences[letter] += 1
    sorted_words_by_score = []
    for word in words:
        unique_letter_frequencies = 0
        for letter in set(word):
            unique_letter_frequencies += letter_frequences[letter]
        heapq.heappush(sorted_words_by_score, (-unique_letter_frequencies, word))

    best_words = [heapq.heappop(sorted_words_by_score)[1] for _ in range(100)]
    return best_words


good_starting_words = determine_starting_words(five_letter_words)

GOOD = 'G'
OTHER_POSITION = 'O'
NOT_IN_WORD = 'X'

COLOURS = {
    GOOD: '\033[92m',
    OTHER_POSITION: '\033[93m',
    NOT_IN_WORD: '\033[91m',
}
END_COLOUR = '\033[0m'


class Knowledge(object):
    def __init__(self, size=WORD_LENGTH):
        a_z = set(string.ascii_uppercase)
        self.letter_in_word = set()
        self.possible_letters = [a_z] * size

    def copy(self):
        k = Knowledge(len(self.possible_letters))
        k.letter_in_word = self.letter_in_word.copy()
        k.possible_letters = [x.copy() for x in self.possible_letters]
        return k

    def __str__(self):
        return f'{self.letter_in_word} + {self.possible_letters}'


def check_match(target, guess):
    result = []
    for i in range(WORD_LENGTH):
        other_letters = [target[x] for x in range(WORD_LENGTH) if x != i]
        if guess[i] == target[i]:
            result.append(GOOD)
        elif guess[i] in other_letters:
            result.append(OTHER_POSITION)
        else:
            result.append(NOT_IN_WORD)
    return result


def new_knowledge(knowledge, guess, result):
    knowledge = knowledge.copy()
    for i in range(WORD_LENGTH):
        guess_letter = guess[i]
        if result[i] == GOOD:
            knowledge.possible_letters[i] = set(guess_letter)
        elif result[i] == OTHER_POSITION:
            knowledge.possible_letters[i] -= set(guess_letter)
            knowledge.letter_in_word.add(guess_letter)
        elif result[i] == NOT_IN_WORD:
            for j in range(WORD_LENGTH):
                knowledge.possible_letters[j] -= set(guess_letter)
    return knowledge


def matches_knowledge(knowledge, possible):
    for i in range(len(possible)):
        if possible[i] not in knowledge.possible_letters[i]:
            return False
    for letter in knowledge.letter_in_word:
        if letter not in possible:
            return False
    return True


def filter_possibilities(possibilities, knowledge):
    return [p for p in possibilities if matches_knowledge(knowledge, p)]


def best_guess(possibilities, knowledge, round):
    if round == 1:
        return random.choice(good_starting_words)

    possible_guesses = filter_possibilities(good_starting_words, knowledge)
    if len(possibilities) <= 100 or len(possible_guesses) == 0:
        possible_guesses += random.sample(possibilities, min(len(possibilities), 100))

    best = ''
    best_reduction = float('inf')

    for guess in possible_guesses:
        outcomes = []
        possible_targets = random.sample(possibilities, min(len(possibilities), 100))
        for possible_target in possible_targets:
            _, new_possibilities, _ = make_guess(guess,
                                                 possible_target,
                                                 possibilities,
                                                 knowledge)
            outcomes.append(len(new_possibilities))
        # TODO - better than mean
        mean_outcome = statistics.mean(outcomes) / len(possibilities)
        if mean_outcome < best_reduction:
            best = guess
            best_reduction = mean_outcome

    return best


def make_guess(guess, target, possibilities, knowledge):
    result = check_match(target, guess)
    knowledge = new_knowledge(knowledge, guess, result)
    possibilities = filter_possibilities(possibilities, knowledge)
    return result, possibilities, knowledge


def solve(target):
    possibilities = five_letter_words.copy()
    knowledge = Knowledge()
    round = 0
    guesses = []
    solved = False
    while not solved:
        round += 1
        guess = best_guess(possibilities, knowledge, round)
        guesses.append(guess)
        result, possibilities, knowledge = make_guess(guess, target, possibilities, knowledge)
        if DEBUG:
            print(guess, len(possibilities), possibilities[:10])
        solved = result == [GOOD] * WORD_LENGTH
    return guesses


def format_result(guess, result):
    coloured_guess = ""
    for i in range(WORD_LENGTH):
        color = COLOURS[result[i]]
        coloured_guess += f'{color}{guess[i]}{END_COLOUR}'
    return coloured_guess


def print_solution(target, guesses):
    for guess in guesses:
        result = check_match(target, guess)
        print(format_result(guess, result))


n_guesses = []
for _ in range(100):
    target = random.choice(five_letter_words)
    guesses = solve(target)
    print_solution(target, guesses)
    print()
    n_guesses.append(len(guesses))

if len(n_guesses) > 0:
    print(statistics.mean(n_guesses))
