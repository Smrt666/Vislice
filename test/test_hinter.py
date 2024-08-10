import unittest

from src.solver.hinter import HintedGame, make_hint


class TestHintedGame(unittest.TestCase):
    def test_make_hint(self) -> None:
        self.assertEqual(make_hint("abc"), "a__")
        self.assertEqual(make_hint("aBCA"), "a__a")
        self.assertEqual(make_hint("abca"), "a__a")
        self.assertEqual(make_hint("Abcda"), "a___a")
        self.assertEqual(make_hint("a"), "a")

    def test_grouping(self) -> None:
        game = HintedGame(["abc", "bac", "cab"])
        self.assertEqual(
            game.groups,
            {
                (3, "a", ((0,),)): ["abc"],
                (3, "b", ((0,),)): ["bac"],
                (3, "c", ((0,),)): ["cab"],
            },
        )
        game = HintedGame(["abca", "abda", "Cabc", "dab"])
        self.assertEqual(
            game.groups,
            {
                (4, "a", ((0, 3),)): ["abca", "abda"],
                (4, "c", ((0, 3),)): ["Cabc"],
                (3, "d", ((0,),)): ["dab"],
            },
        )

    def test_strategize(self) -> None:
        """Just test that it runs without errors."""
        words = ["xabc", "xbac", "xcab", "abc"]
        game = HintedGame(words)
        game.strategize(print_progress=False)
        xstrat = game.get_strat_by_hint("x___")
        self.assertEqual(xstrat.start.json_or_won(), ["abcx", {"xbac": "WON!", "xcab": "WON!", "xabc": "WON!"}])
        astrat = game.get_strat_by_hint("a__")
        self.assertEqual(astrat.start.json_or_won(), ["abc", {"abc": "WON!"}])
