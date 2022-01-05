import random
import re
import statistics
import string

WORD_LENGTH = 5

five_letter_regex = re.compile(r'^[a-z]{5}$')  # Only match lower-case words
five_letter_words = []
with open('/usr/share/dict/words', 'r') as dictionary:
    for word in dictionary:
        if five_letter_regex.match(word):
            five_letter_words.append(word.strip())

GOOD = 'G'
OTHER_POSITION = 'O'
NOT_IN_WORD = 'X'


class Knowledge(object):
    def __init__(self, size=WORD_LENGTH):
        a_z = set(string.ascii_lowercase)
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


def best_guess(possibilities, knowledge):
    best = ''
    best_reduction = float('inf')
    possible_guesses = random.sample(possibilities, min(len(possibilities), 100))
    for guess in possible_guesses:
        guess = random.choice(possibilities)

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
        print(guess, mean_outcome)
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
        guess = best_guess(possibilities, knowledge)
        guesses.append(guess)
        result, possibilities, knowledge = make_guess(guess, target, possibilities, knowledge)
        solved = result == [GOOD] * WORD_LENGTH
    return guesses


n_guesses = []
for _ in range(1):
    target = random.choice(five_letter_words)
    guesses = solve(target)
    print(target, guesses)
    n_guesses.append(len(guesses))

print(statistics.mean(n_guesses))
