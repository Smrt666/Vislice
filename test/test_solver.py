import unittest

from solver.game import GameStateTree, get_tti, Strategy


class TestGameStateTree(unittest.TestCase):
    def assertSolveEqual(self, left: tuple[int, str], right: tuple[int, str]) -> None:
        self.assertEqual(left[0], right[0])
        self.assertCountEqual(left[1], right[1])

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

    def test_solve_single_word(self) -> None:
        tree = GameStateTree(["abc"], "abcd")
        self.assertSolveEqual(tree.solve((0,), ""), (0, "abc"))
        self.assertSolveEqual(tree.solve((0,), "d"), (0, "abc"))

    def test_solve_trivial(self) -> None:
        tree = GameStateTree(["abc", "bac", "cab"], "abcd")
        self.assertSolveEqual(tree.solve((0, 1, 2), ""), (0, "abc"))

        tree = GameStateTree(["abc", "baa", "cab"], "abc")
        self.assertSolveEqual(tree.solve((0, 1, 2), ""), (0, "ab"))
        self.assertSolveEqual(tree.solve((0, 2), "ab"), (0, "c"))

        tree = GameStateTree(["ababa", "babab", "bacba", "dacdc"], "abcd")
        self.assertSolveEqual(tree.solve((0, 1, 2, 3), ""), (0, "a"))
        tree.memo.clear()
        self.assertSolveEqual(tree.solve((0, 1, 2), ""), (0, "ab"))

    def test_solve_general(self) -> None:
        tree = GameStateTree(["ababa", "babab", "bacba", "dacdc", "cbdcb", "bdddd", "bbbbb"], "abcd")
        self.assertSolveEqual(tree.solve(tuple(range(7)), ""), (1, "a"))
        self.assertSolveEqual(tree.solve((4, 5, 6), ""), (0, "b"))

        tree = GameStateTree(["ababa", "babab", "bacba", "dacdc", "cbdcb", "bdddd", "bbbbb", "ccccc"], "abcd")
        self.assertSolveEqual(tree.solve(tuple(range(8)), ""), (1, "b"))

        tree = GameStateTree(["ababa", "babab", "bacba", "dacdc", "cbdcb", "bdddd", "bbbbb", "ccccc", "ddddd"], "abcd")
        self.assertSolveEqual(tree.solve(tuple(range(9)), ""), (2, "b"))

        tree = GameStateTree(["aa", "bb", "cc", "dd"], "abcd")
        self.assertSolveEqual(tree.solve((0, 1, 2, 3), ""), (3, "a"))

        tree = GameStateTree(["baa", "bbb", "ccb", "ddb"], "abcd")
        self.assertSolveEqual(tree.solve((0, 1, 2, 3), ""), (1, "b"))

        tree = GameStateTree(["abd", "abe", "acf", "acg", "hbd", "hbe", "hcf", "hcg"], "abcdefgh")
        self.assertSolveEqual(tree.solve(tuple(range(8)), ""), (3, "a"))

    def test_extract_strategy(self) -> None:
        # Writing this tests is a pain. If the code is broken this will fail.
        # If there are bugs this will probably not fail. Choice depends on this heavily.
        # If there are bugs in this code, Choice will not work.
        tree = GameStateTree(["baa", "bbb", "ccb", "ddb"], "abcd")
        tree.solve_all()
        self.assertEqual(
            tree.extract_strategy(), {("", 0): "b", ("b", 0): "a", ("b", 1): "", ("b", 2): "c", ("bc", 2): "", ("bc", 3): "d"}
        )

        tree = GameStateTree(["abc", "bac", "cab"], "abc")
        tree.solve_all()
        self.assertEqual(tree.extract_strategy(), {("", 0): "abc"})


class TestChoice(unittest.TestCase):
    def test_shallow(self) -> None:
        strat = Strategy(["abc", "bac", "cab"])
        self.assertEqual(str(strat.start), "['abc', {'bac': 'WON!', 'cab': 'WON!', 'abc': 'WON!'}]")

        strat = Strategy(["abd", "abe", "acf", "acg", "hbd", "hbe", "hcf", "hcg"])
        self.assertEqual(
            strat.start.json_or_won(),
            [
                "a",
                {
                    "___": [
                        "h",
                        {
                            "h__": [
                                "b",
                                {
                                    "hb_": ["d", {"hbd": "WON!", "hb_": ["e", {"hbe": "WON!"}]}],
                                    "h__": ["c", {"hc_": ["f", {"hcf": "WON!", "hc_": ["g", {"hcg": "WON!"}]}]}],
                                },
                            ]
                        },
                    ],
                    "a__": [
                        "b",
                        {
                            "ab_": ["d", {"abd": "WON!", "ab_": ["e", {"abe": "WON!"}]}],
                            "a__": ["c", {"ac_": ["f", {"acf": "WON!", "ac_": ["g", {"acg": "WON!"}]}]}],
                        },
                    ],
                },
            ],
        )
