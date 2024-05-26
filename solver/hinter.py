from solver.game import WordShape, get_tti, Strategy
from typing import Any


def make_hint(word: str) -> str:
    """Create a hint for a word."""
    word = word.lower()
    return "".join([char if char == word[0] else "_" for char in word])


def key_to_hint(key: tuple[int, str, WordShape]) -> str:
    """Convert a key to a hint."""
    chars = ["_"] * key[0]
    for i in key[2][0]:
        chars[i] = key[1][0]
    return "".join(chars)


class HintedGame:
    """A game with hinted first letter of each word. It also allows different lengths of words."""

    def __init__(self, words: list[str]) -> None:
        self.words = list(words)
        self.word_keys: dict[str, tuple[int, str, WordShape]] = {
            word: (len(word), word[0], get_tti(word, word[0])) for word in map(str.lower, self.words)
        }
        self.groups: dict[tuple[int, str, WordShape], list[str]] = {key: [] for key in self.word_keys.values()}
        for word in self.words:
            self.groups[self.word_keys[word.lower()]].append(word)
        self.strategies: dict[tuple[int, str, WordShape], Strategy] = {}

    def strategize(self, print_progress: bool = True) -> None:
        """Create strategies for each group of words."""
        if self.strategies:
            return
        self.strategies: dict[tuple[int, str, WordShape], Strategy] = {}
        for i, key in enumerate(self.groups):
            self.strategies[key] = Strategy(self.groups[key])
            if print_progress:
                print(f"Strategized {i + 1}/{len(self.groups)} groups." + " " * 10, end="\r")

    def get_strat_by_hint(self, hint: str) -> Strategy:
        """Return the strategy for a given hint. (Hint looks like 'a__a_')"""
        hint = hint.lower()
        return self.strategies[(len(hint), hint[0], get_tti(hint, hint[0]))]

    def json(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary of the object."""
        return {"words": self.words, "strategies": {key_to_hint(key): strat.json() for key, strat in self.strategies.items()}}
