from typing import Callable


"""
Every word gets triple representation:
 - id as a number
 - string  # lower/upper case is not important for hangman, so every word is converted to lower case
 - tti: tuple of tuples of integers: for each letter a tuple tells the positions of the letter in the word
"""


def get_tti(word: str, alphabet: str) -> tuple[tuple[int, ...], ...]:
    """Returns the tti of the word."""
    return tuple(tuple(i for i, c in enumerate(word) if c == letter) for letter in alphabet)


def memoize(
    func: Callable[["GameStateTree", tuple[int, ...], str], tuple[int, str]],
) -> Callable[["GameStateTree", tuple[int, ...], str], tuple[int, str]]:
    """Memoization decorator specifically for GameStateTree.solve."""

    def wrapper(self: "GameStateTree", word_list: tuple[int, ...], used_letters: str) -> tuple[int, str]:
        key = used_letters, min(word_list)
        if key in self.memo:
            return self.memo[key]
        result = func(self, word_list, used_letters)
        self.memo[key] = result
        return result

    return wrapper


class GameStateTree:
    """An object containing the words in all representations and memoization table."""

    def __init__(self, words: list[str], alphabet: str) -> None:
        self.original_words: list[str] = list(words)
        self.alphabet: str = str(alphabet).lower()
        self.words: list[str] = list(map(lambda w: str(w).lower(), words))  # ids (pk in code) are the indices in this list
        self.words_tti: list[tuple[tuple[int, ...], ...]] = list(map(lambda w: get_tti(w, alphabet), self.words))
        self.pks = tuple(range(len(self.words)))

        # memoization table: word list (of ids)) -> tuple(minimal number of wrong guesses in worst case, letter to guess)
        # word list can be uniqely represented using only used letters (ordered) and smallest word in the list (lowest id)
        self.memo: dict[tuple[str, int], tuple[int, str]] = dict()

    @memoize
    def solve(self, word_list: tuple[int, ...], used_letters: str) -> tuple[int, str]:
        """Solves the game for the given word list.
        Returns the tuple (minimal number of wrong guesses in worst case, letter(s) to guess)."""
        if not word_list:
            return 0, ""

        # trivial cases
        unused_letters = set(self.alphabet) - set(used_letters)
        shared_letters: set[str] = unused_letters.intersection(*(set(self.words[pk]) for pk in word_list))
        shared_joined = "".join(shared_letters)
        # if all missing letters are in every word, we can guess all of them  - edge case
        if all((set(self.words[pk]) & unused_letters).issubset(shared_letters) for pk in word_list):
            return 0, shared_joined
        # if an unused letter is in all words, it is an obvious choice - nothing can be lost, can only be gained
        if shared_letters:
            max_n = 0
            for group in self.group_words(word_list, [self.alphabet.index(c) for c in shared_letters]):
                n, _ = self.solve(group, used_letters + shared_joined)
                if n > max_n:
                    max_n = n
            return n, shared_joined

        # general case - try all usable letters and choose the best one
        # find letters in which the words differ (positions matter) - usable letters
        list_ttis = [{self.words_tti[pk][i] for pk in word_list} for i in range(len(self.alphabet))]
        usable_letters = [c for i, c in enumerate(self.alphabet) if len(list_ttis[i]) >= 2]
        if not usable_letters:  # all letters were found
            return 0, ""
        min_max_n = len(self.alphabet) + 69  # some big number
        best_letter = ""
        for letter in usable_letters:
            # group the words by the letter's position in the word
            groups = self.group_words(word_list, [self.alphabet.index(letter)])
            results = [self.solve(group, used_letters + letter) for group in groups]
            # get the worst case scenario, i.e. the maximum number of wrong guesses
            # if the letter is not in all of the words of the group, we guessed incorrectly
            max_n = max(results[i][0] + int(all(letter not in self.words[pk] for pk in groups[i])) for i in range(len(groups)))
            if max_n < min_max_n:
                min_max_n = max_n
                best_letter = letter
        return min_max_n, best_letter

    def group_words(self, word_list: tuple[int, ...], letters_i: list[int]) -> list[tuple[int, ...]]:
        """Groups the words by their tti."""
        groups: dict[tuple[tuple[int, ...], ...], list[int]] = {}
        for key, element in zip(
            map(lambda pk: tuple(self.words_tti[pk][letter_i] for letter_i in letters_i), word_list), word_list
        ):
            if key not in groups:
                groups[key] = []
            groups[key].append(element)
        return [tuple(group) for group in groups.values()]
