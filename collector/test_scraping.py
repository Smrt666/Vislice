import unittest
import requests

import io
import contextlib

from collector.sskj_collector import get_sskj_page, extract_words, get_all_words, extract_nouns, sanitize


class TestSSKJCollector(unittest.TestCase):
    """Test if fran hasn't changed their website structure."""

    def test_page_reachable(self):
        response = requests.get("https://www.fran.si/iskanje?FilteredDictionaryIds=130&View=1&Query=%2A")
        self.assertTrue(response.status_code == requests.codes.ok)

    def test_get_sskj_page(self):
        get_sskj_page(1)

    def test_extract_words(self):
        content = get_sskj_page(1)
        words = extract_words(content)
        self.assertTrue(len(words) > 2)
        self.assertIn("a", words)

    def test_extract_nouns(self):
        content = get_sskj_page(1)
        words = extract_nouns(content)
        self.assertTrue(len(words) > 2)
        self.assertIn("ábak", words)

    def test_get_all_words(self):
        words = get_all_words(2, 2, False, extract_words)
        self.assertTrue(len(words) > 2)
        self.assertIn("a", words)

        nouns = get_all_words(2, 2, False, extract_nouns)
        self.assertTrue(len(nouns) > 2)
        self.assertIn("ábak", nouns)

    def test_sanitize(self):
        words = get_all_words(2, 2, False, extract_words)
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            words = sanitize(words)
        self.assertIn("abak", words)
        self.assertTrue(len(words) > 2)

        abc = "abcdefghijklmnoprsštuvzž"
        words = [abc, abc.upper(), "a123", "a b", "w", "="]
        with contextlib.redirect_stdout(f):
            words = sanitize(words)
        self.assertTrue(len(words) == 2)
        self.assertIn(abc, words)
        self.assertIn(abc.upper(), words)
        self.assertIn("Removing 1 words with special characters: ['=']", f.getvalue())
