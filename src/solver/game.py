from typing import Optional, Protocol
import json


"""
Every word gets triple representation:
 - id as a number
 - string  # lower/upper case is not important for hangman, so every word is converted to lower case
 - tti (WordShape): tuple of tuples of integers: for each letter a tuple tells the positions of the letter in the word
"""

"""The best strategy
We define the best strategy as the one that minimizes the number of wrong guesses in the worst case scenario.
"""

"""
Solve strategy:
    - We start with the whole word list and no used letters.
    - We find the best letter to guess:
        * if all words share some letters, we can guess all of them. It is always the best choice: in the worst case
          there is another strategy with the same number of wrong guesses.
        * otherwise, we try all usable letters and choose the best one
        * words are grouped by the position of that letter in the word
        * we recursively call the solve function for each group

Optimizations on solve
 - memoization: we store the results of the solve function in a table
    * When trying letters order is important, but the order for the same group is not. So we can memoize the results.
    * We can uniquely represent the group using only used letters (sorted) and the smallest word in the list.
 - killing branches: if we know that a branch will not be the best, we can kill it before calculating everything
    * if already found a solution with n wrong guesses, we can kill the branch if it has n or more wrong guesses
    * the killing can be done when recursively solving the groups. The cost (number of wrong guesses) for the letter
      can only increase, so we don't need to calculate the rest of the groups if we already have a better solution.
    * we start solving for groups that are likely to give the worst results, because we can kill them sooner
      The largest groups are likely to give the worst results, so we start with them. Starting with the the group
      without the guessed letter did not seem to work that well.
    * when trying letters, we start with the most frequent ones, because they are likely to give better results
      The sooner we get better results for letters, the more branches can we kill.
      Sorting letters by size of the largest group and the size of the group without the letter did not seem to work that well.
"""

type WordShape = tuple[tuple[int, ...], ...]
type ChoiceJSON = list[str | dict[str, "ChoiceJSON"]] | str


class SGTSolveFunc(Protocol):
    def __call__(
        _self, self: "GameStateTree", word_list: tuple[int, ...], used_letters: str, *, kill_after: Optional[int] = None
    ) -> tuple[int, str]: ...


def get_tti(word: str, alphabet: str) -> WordShape:
    """Returns the tti of the word."""
    return tuple(tuple(i for i, c in enumerate(word) if c == letter) for letter in alphabet)


def memoize(func):
    """Memoization decorator specifically for GameStateTree.solve."""

    def wrapper(
        self: "GameStateTree", word_list: tuple[int, ...], used_letters: str, *, kill_after: int | None = None
    ) -> tuple[int, str]:
        key = "".join(sorted(used_letters)), min(word_list)
        if key in self.memo:
            return self.memo[key]

        if kill_after is not None and kill_after <= 0:
            self.killed[key] = 0
            return 0, ""
        if kill_after is not None and key in self.killed and self.killed[key] >= kill_after:
            return self.killed[key], ""

        result = func(self, word_list, used_letters, kill_after=kill_after)
        if kill_after is not None and result[0] >= kill_after:
            self.killed[key] = result[0]
        else:
            self.memo[key] = result
        return result

    return wrapper


def get_word_shape(pk: int, words_tti: list[WordShape], letters_i: list[int]) -> WordShape:
    """For a given word returns positions of the letters in that word."""
    return tuple(words_tti[pk][letter_i] for letter_i in letters_i)


class GameStateTree:
    """An object containing the words in all representations and memoization table."""

    def __init__(self, words: list[str], alphabet: str) -> None:
        self.original_words: list[str] = list(words)
        self.alphabet: str = str(alphabet).lower()
        self.words: list[str] = list(map(lambda w: str(w).lower(), words))  # ids (pk in code) are the indices in this list
        self.words_tti: list[WordShape] = list(map(lambda w: get_tti(w, alphabet), self.words))
        self.pks = tuple(range(len(self.words)))

        # memoization table: word list (of ids)) -> tuple(minimal number of wrong guesses in worst case, letter to guess)
        # word list can be uniqely represented using only used letters (ordered) and smallest word in the list (lowest id)
        self.memo: dict[tuple[str, int], tuple[int, str]] = dict()
        self.killed: dict[tuple[str, int], int] = dict()  # word -> lower bound of wrong guesses
        self.dependency: dict[tuple[str, int], list[tuple[str, int]]] = dict()  # memoization dependency graph
        # dependency: (used_letters, min_word_id) -> [(used_letters, min_word_id), ...]
        # used_letters must be sorted

    @memoize
    def solve(self, word_list: tuple[int, ...], used_letters: str, *, kill_after: Optional[int] = None) -> tuple[int, str]:
        """Solves the game for the given word list.
        Returns the tuple (minimal number of wrong guesses in worst case, letter(s) to guess)."""
        used_letters = "".join(sorted(used_letters))
        key = used_letters, min(word_list)
        if not word_list:
            return 0, ""

        # trivial cases
        unused_letters = set(self.alphabet) - set(used_letters)
        if kill_after is None:
            kill_after = len(unused_letters) + 1  # infinity
        shared_letters: set[str] = unused_letters.intersection(*(set(self.words[pk]) for pk in word_list))
        shared_joined = "".join(sorted(shared_letters))
        # if all missing letters are in every word, we can guess all of them  - edge case
        if all((set(self.words[pk]) & unused_letters).issubset(shared_letters) for pk in word_list):
            return 0, shared_joined
        # if an unused letter is in all words, it is an obvious choice - nothing can be lost, can only be gained
        if shared_letters:
            max_n = 0
            self.dependency[key] = []
            for group in self.group_words(word_list, [self.alphabet.index(c) for c in shared_letters]):
                used_shared = "".join(sorted(used_letters + shared_joined))
                n, _ = self.solve(group, used_shared, kill_after=kill_after)
                self.dependency[key].append((used_shared, min(group)))
                if n > max_n:
                    max_n = n
            return max_n, shared_joined

        # general case - try all usable letters and choose the best one
        # find letters in which the words differ (positions matter) - usable letters
        list_ttis = [{self.words_tti[pk][i] for pk in word_list} for i in range(len(self.alphabet))]
        usable_letters = [c for i, c in enumerate(self.alphabet) if len(list_ttis[i]) >= 2]
        if not usable_letters:  # all letters were found
            return 0, ""
        min_max_n = min(len(unused_letters) + 1, kill_after)  # some big number
        best_letter = ""
        kill_child = kill_after
        # start with the most frequent letters, that is a good strategy
        # the sooner we get better results, the better - more branches can be killed sooner
        letter_frequency = {letter: sum(self.words[i].count(letter) for i in word_list) for letter in usable_letters}
        for letter in sorted(usable_letters, key=lambda c: letter_frequency[c], reverse=True):
            # group the words by the letter's position in the word
            groups = self.group_words(word_list, [self.alphabet.index(letter)])
            max_n = 0
            group_enumeration = enumerate(groups)
            group_enumeration = sorted(group_enumeration, key=lambda i_group: len(i_group[1]), reverse=True)
            for i, group in group_enumeration:
                # if the letter is not in all of the words of the group, we guessed incorrectly
                errors = int(all(letter not in self.words[pk] for pk in groups[i]))
                result = self.solve(group, used_letters + letter, kill_after=kill_child - errors)
                value = result[0] + errors
                # get the worst case scenario, i.e. the maximum number of wrong guesses
                if max_n < value:
                    max_n = value
                    if max_n >= kill_child:
                        break
            if max_n < kill_child:
                kill_child = max_n
            # we are minimizing the worst case scenario
            if max_n < min_max_n:
                min_max_n = max_n
                best_letter = letter
                self.dependency[key] = [("".join(sorted(used_letters + letter)), min(group)) for group in groups]
        return min_max_n, best_letter

    def group_words(self, word_list: tuple[int, ...], letters_i: list[int]) -> list[tuple[int, ...]]:
        """Groups the words by their tti."""
        groups: dict[WordShape, list[int]] = {}
        for key, element in zip(map(lambda pk: get_word_shape(pk, self.words_tti, letters_i), word_list), word_list):
            if key not in groups:
                groups[key] = []
            groups[key].append(element)
        return [tuple(group) for group in groups.values()]

    def solve_all(self) -> tuple[int, str]:
        """Solves the game for all words. The same as calling solve for all words with no starting used letters."""
        return self.solve(self.pks, "")

    def _extract_strategies(self, root: tuple[str, int], result_list: list[dict[tuple[str, int], str]]) -> None:
        _, letters = self.memo[root]
        result_list.append({root: letters})
        if root not in self.dependency:
            return
        for dependency in self.dependency[root]:
            self._extract_strategies(dependency, result_list)

    def extract_strategy(self, root: tuple[str, int] = ("", 0)) -> dict[tuple[str, int], str]:
        """Extracts the strategy from the memoization table. root's used_letters should sorted.
        All it does is recursively extract the minimal sufficient number of decisions from the memoization table."""
        if not self.memo:
            # solve_all has not been run. It can be computationally expensive, so it is not executed implicitly.
            raise LookupError("No strategy found. Please run solve_all first.")
        _, letters = self.memo[root]
        result = {root: letters}
        results: list[dict[tuple[str, int], str]] = []
        if root not in self.dependency:
            return result
        for dependency in self.dependency[root]:
            self._extract_strategies(dependency, result_list=results)
        for d in results:
            result.update(d)
        return result


class Strategy:
    """A class for managing strategies."""

    def __init__(self, tree: GameStateTree | list[str]) -> None:
        """Initializes the strategy from a tree or a list of words.
        If a list of words is provided, it is converted to a tree and solve_all is called.
        Attribute start can be used to access the root of the decision tree, which is of type Choice."""

        if isinstance(tree, list):
            wordlen = len(tree[0])
            assert (len(word) == wordlen for word in tree), "All words should have the same length."
            alphabet = set.union(*(set(word.lower()) for word in tree))
            alphabet = "".join(sorted(alphabet))
            tree = GameStateTree(tree, alphabet)
            tree.solve_all()
        self.original_words: list[str] = tree.original_words.copy()
        self.alphabet: str = tree.alphabet
        self.words: list[str] = tree.words.copy()
        self.words_tti: list[WordShape] = tree.words_tti.copy()

        self.strategy: dict[tuple[str, int], str] = tree.extract_strategy()
        self.max_errors, _ = tree.solve_all()
        self.start = Choice("", list(tree.pks), self)

    def get_strategy(self, word_list: list[int], used_letters: str) -> str:
        """Returns the best letter to guess.
        Assumes that word_list makes sense in the context of the used_letters.
        - i.e. all of these letters are in the same positions."""
        used_letters = "".join(sorted(used_letters))
        return self.strategy[used_letters, min(word_list)]

    def json(self) -> dict[str, ChoiceJSON | list[str] | int | str]:
        return {
            "max_errors": self.max_errors,
            "alphabet": self.alphabet,
            "words": self.words,
            "strategy": self.start.json_or_won(),
        }


class Choice:
    """A tree strategy representation."""

    def __init__(self, used_letters: str, word_list: list[int], strategy: Strategy) -> None:
        """Initializes the choice. With the help of the strategy, it initializes
        all later choices that may be needed when following the optimal strategy."""
        assert word_list, "Choice should have at least one word"

        self.strategy: Strategy = strategy
        self.used_letters: str = "".join(sorted(used_letters))
        self.word_list: list[int] = word_list

        self.choice: str
        self.shapes: list[WordShape]
        self.letterids: list[int]
        self.children: dict[WordShape, Choice]

        if set.union(*(set(strategy.words[pk]) for pk in word_list)).issubset(set(used_letters)):
            # all letters were found
            self.choice = ""
            self.letterids = []
            self.shapes = []
            self.children = {}
            return

        # recursive initialization of the children - all poosible future choices
        self.choice = self.strategy.get_strategy(
            word_list=word_list,
            used_letters=used_letters,
        )
        self.letterids = [self.strategy.alphabet.index(letter) for letter in self.choice]
        shapes = [get_word_shape(pk, self.strategy.words_tti, self.letterids) for pk in word_list]
        self.shapes = list(set(shapes))
        shape_words: dict[WordShape, list[int]] = {shape: [] for shape in self.shapes}
        for shape, pk in zip(shapes, word_list):
            shape_words[shape].append(pk)
        self.children = {shape: Choice(used_letters + self.choice, shape_words[shape], strategy) for shape in self.shapes}

    def word_shape(self, word: str) -> WordShape:
        """Slow for calling multiple times."""
        pk = self.strategy.words.index(word)
        return get_word_shape(pk, self.strategy.words_tti, self.letterids)

    def move(self, word: str) -> "Choice":
        return self.children[self.word_shape(word)]

    def possible_words(self) -> list[str]:
        return [self.strategy.words[pk] for pk in self.word_list]

    def json_or_won(self) -> ChoiceJSON:
        if self.choice == "":
            return "WON!"

        word = ["_"] * len(self.strategy.words[self.word_list[0]])
        used_ids = [self.strategy.alphabet.index(c) for c in self.used_letters]
        common_shape = get_word_shape(self.word_list[0], self.strategy.words_tti, used_ids)
        for i, c in zip(common_shape, self.used_letters):
            for j in i:
                word[j] = c
        all_shapes = [word.copy() for _ in self.shapes]
        for pos, shape in enumerate(self.shapes):
            for i, c in zip(shape, self.choice):
                for j in i:
                    all_shapes[pos][j] = c
        all_shapes = ["".join(shape) for shape in all_shapes]
        return [self.choice, {all_shapes[i]: self.children[shape].json_or_won() for i, shape in enumerate(self.shapes)}]

    def __str__(self) -> str:
        return json.dumps(self.json_or_won())
