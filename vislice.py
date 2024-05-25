import argparse

from collector.sskj_collector import get_all_words, sanitize, extract_nouns, extract_words
from collector.usage_counter import words_usage
from solver.game import Strategy

import json
import time

parser = argparse.ArgumentParser(description="Script for this project.")
subparsers = parser.add_subparsers(help="sub-command help", dest="action")

# sskjcollect
sskjcollect_parser = subparsers.add_parser("sskjcollect", help="collect words from SSKJ")
sskjcollect_parser.add_argument(
    "--limit",
    action="store",
    type=int,
    default=None,
    help="limit the number of pages to collect words from (default: all)",
)
sskjcollect_parser.add_argument(
    "--threads",
    action="store",
    type=int,
    default=100,
    help="maximum number of threads to use (default: 100)",
)
sskjcollect_parser.add_argument(
    "--noprogress",
    action="store_true",
    default=False,
    help="show progress while collecting words (default)",
)
sskjcollect_parser.add_argument(
    "--file",
    action="store",
    type=argparse.FileType("w+", encoding="UTF-8"),
    default="data/sskj_words.txt",
    help="file to save words to (default: data/sskj_words.txt)",
)
sskjcollect_parser.add_argument(
    "--raw",
    action="store_true",
    default=False,
    help="by default it removes accents, special characters, ...",
)
sskjcollect_parser.add_argument(
    "--nounsonly",
    action="store_true",
    default=False,
    help="collect only nouns",
)

# getstrategy
getstrategy_parser = subparsers.add_parser("getstrategy", help="Find strategy for a word list.")
getstrategy_parser.add_argument(
    "length",
    action="store",
    type=int,
    help="length of words to find strategy for",
)
getstrategy_parser.add_argument(
    "words",
    action="store",
    type=argparse.FileType("r", encoding="UTF-8"),
    help="file with words to find strategy for",
)
getstrategy_parser.add_argument(
    "--output",
    action="store",
    type=argparse.FileType("w+", encoding="UTF-8"),
    default="data/strategy.json",
    help="file to save strategy to (default: data/strategy.json)",
)
getstrategy_parser.add_argument(
    "--limit",
    action="store",
    type=int,
    default=None,
    help="limit the number of words to find strategy for (default: all)",
)

# usage
usage_parser = subparsers.add_parser("usage", help="Count usage of words. Format: word,count <newline> word,count <newline>...")
usage_parser.add_argument(
    "words",
    action="store",
    type=argparse.FileType("r", encoding="UTF-8"),
    help="file with words to count usage for",
)
usage_parser.add_argument(
    "--lang",
    action="store",
    type=str,
    default="sl",
    help="language of the search engine (default: sl)",
)
usage_parser.add_argument(
    "--threads",
    action="store",
    type=int,
    default=100,
    help="maximum number of threads to use (default: 100)",
)
usage_parser.add_argument(
    "--noprogress",
    action="store_true",
    default=False,
    help="show progress while counting usage (default)",
)
usage_parser.add_argument(
    "--output",
    action="store",
    type=argparse.FileType("w+", encoding="UTF-8"),
    default="data/usage.csv",
    help="file to save usage to (default: data/usage.csv)",
)
usage_parser.add_argument(
    "--sort",
    action="store_true",
    default=False,
    help="sort the words by usage (default: False)",
)

# run all tests
runtests_parser = subparsers.add_parser("test", help="Run all tests.")
runtests_parser.add_argument(
    "--out",
    action="store",
    type=argparse.FileType("w+", encoding="UTF-8"),
    default=None,
    help="file to save test results to (default: stdout)",
)

# The beautiful match-case statement that puts everything together
match args := parser.parse_args():
    case argparse.Namespace(
        action="sskjcollect",
        nounsonly=nounsonly,
        raw=raw,
        limit=limit,
        threads=threads,
        noprogress=noprogress,
        file=file,
    ):
        progress = not noprogress
        target = "nouns" if nounsonly else "words"
        print(
            f"Collecting {target} from SSKJ with raw={raw}, limit={limit},"
            + f" threads={threads}, progress={progress}, file={file.name}..."
        )

        extractor = extract_nouns if nounsonly else extract_words
        words = get_all_words(lim=limit, max_threads=threads, print_progress=progress, word_extractor=extractor)
        if not raw:
            words = sanitize(words)

        file.write("\n".join(words))
        file.close()
        print(f"Stored {len(words)} words into {file.name}")
    case argparse.Namespace(action="getstrategy", length=length, words=words, output=output, limit=limit):
        print(f"Finding strategy for words in {words.name}...")
        words = [str(line.strip()) for line in words.read().split()]  # split by whitespace
        words = [word for word in words if len(word) == length]
        if limit is not None:
            words = words[:limit]

        print(f"Found {len(words)} words to find strategy for. Computing strategy... (Might take a while.)")
        time0 = time.time()
        strategy = Strategy(words)
        print(f"Strategy found. Maximal number of wrong guessess is {strategy.max_errors}. Saving to {output.name}...")
        output.write(json.dumps(strategy.json(), indent=1, ensure_ascii=False))
        print(f"Stored strategy for {len(words)} words into {output.name}. Took {time.time() - time0:.2f} seconds.")
    case argparse.Namespace(action="test", out=out):
        import unittest

        runner = unittest.TextTestRunner(verbosity=2, stream=out)

        print("Running tests in test/  (code correctness tests)")
        main_suite = unittest.TestLoader().discover("test")
        runner.run(main_suite)

        print("\nRunning tests in collector/  (unchanged website structure tests)")
        collector_suite = unittest.TestLoader().discover("collector")
        runner.run(collector_suite)

    case argparse.Namespace(
        action="usage", words=words, lang=lang, threads=threads, noprogress=noprogress, output=output, sort=sort
    ):
        print(f"Counting usage of words in {words.name}...")

        words = [str(line.strip()) for line in words.read().split("\n")]

        print(f"Found {len(words)} words to count usage for. Googling...")
        usage = words_usage(words, lang, threads, not noprogress)

        if sort:
            usage = sorted(usage.items(), key=lambda item: item[1], reverse=True)
        else:
            usage = usage.items()

        print(f"Usage counted. Saving to {output.name}...")
        output.write("\n".join([f"{word},{count}" for word, count in usage]))

        print("Done.")

    case _:
        print(f"Unsupported command arguments: {vars(args)}")
        parser.print_help()
