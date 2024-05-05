import unittest

from solver.game import GameStateTree, get_tti


class TestGameStateTree(unittest.TestCase):
    def test_get_tti(self) -> None:
        self.assertEqual(get_tti("abc", "abc"), ((0,), (1,), (2,)))
        self.assertEqual(get_tti("abacaba", "abc"), ((0, 2, 4, 6), (1, 5), (3,)))
        self.assertEqual(get_tti("abacaba", "bacd"), ((1, 5), (0, 2, 4, 6), (3,), ()))
        self.assertEqual(get_tti("", "bacde"), ((), (), (), (), ()))

    def test_init(self) -> None:
        tree = GameStateTree(["abc", "Aaa", "aCa"], "abcd")
        self.assertEqual(tree.original_words, ["abc", "Aaa", "aCa"])
        self.assertEqual(tree.alphabet, "abcd")
        self.assertEqual(tree.words, ["abc", "aaa", "aca"])
        self.assertEqual(tree.words_tti, [((0,), (1,), (2,), ()), ((0, 1, 2), (), (), ()), ((0, 2), (), (1,), ())])
        self.assertEqual(tree.pks, (0, 1, 2))
        self.assertEqual(tree.memo, dict())

    def test_group_words(self) -> None:
        tree = GameStateTree(["aba", "Aaa", "ACa"], "abcd")
        self.assertCountEqual(tree.group_words((0, 1, 2), [0, 1]), [(0,), (1,), (2,)])
        self.assertCountEqual(tree.group_words((0, 1, 2), [0]), [(0, 2), (1,)])
        self.assertCountEqual(tree.group_words((0, 1, 2), [0, 3]), [(0, 2), (1,)])
        self.assertCountEqual(tree.group_words((0, 1, 2), [3]), [(0, 1, 2)])
        self.assertCountEqual(tree.group_words((0,), [3]), [(0,)])
