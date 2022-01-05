import random
import re
import string

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
    def __init__(self, size=5):
        a_z = set(string.ascii_lowercase)
        self.letter_in_word = set()
        self.possible_letters = [a_z] * size

    def __str__(self):
        return f'{self.letter_in_word} + {self.possible_letters}'


def check_match(target, guess):
    result = []
    for i in range(len(guess)):
        other_letters = [target[x] for x in range(len(target)) if x != i]
        if guess[i] == target[i]:
            result.append(GOOD)
        elif guess[i] in other_letters:
            result.append(OTHER_POSITION)
        else:
            result.append(NOT_IN_WORD)
    return result


def new_knowledge(knowledge, guess, result):
    for i in range(len(guess)):
        guess_letter = guess[i]
        if result[i] == GOOD:
            knowledge.possible_letters[i] = set(guess_letter)
        elif result[i] == OTHER_POSITION:
            knowledge.letter_in_word.add(guess_letter)
        elif result[i] == NOT_IN_WORD:
            for j in range(len(knowledge.possible_letters)):
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


def solve(target):
    possibilities = five_letter_words.copy()
    knowledge = Knowledge()
    round = 0
    guesses = []
    while len(possibilities) > 1:
        round += 1
        guess = random.choice(possibilities)  # TODO: Do better than a random guess
        guesses.append(guess)
        result = check_match(target, guess)
        knowledge = new_knowledge(knowledge, guess, result)
        possibilities = filter_possibilities(possibilities, knowledge)
    return list(possibilities)[0], round, guesses


print(solve('tiger'))

for games in range(100):
    target = random.choice(five_letter_words)
    print(solve(target))
