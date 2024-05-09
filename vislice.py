import argparse

from collector.sskj_collector import get_all_words, sanitize
from solver.game import Strategy

import json

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


match args := parser.parse_args():
    case argparse.Namespace(
        action="sskjcollect",
        raw=raw,
        limit=limit,
        threads=threads,
        noprogress=noprogress,
        file=file,
    ):
        progress = not noprogress
        print(
            f"Collecting words from SSKJ with raw={raw}, limit={limit},"
            + f" threads={threads}, progress={progress}, file={file.name}..."
        )

        words = get_all_words(lim=limit, max_threads=threads, print_progress=progress)
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
        print(words)
        strategy = Strategy(words)
        print(f"Strategy found. Maximal number of wrong guessess is {strategy.max_errors}. Saving to {output.name}...")
        output.write(json.dumps(strategy.start.json_or_won(), indent=1, ensure_ascii=False))
        print(f"Stored strategy for {len(words)} words into {output.name}.")
    case _:
        print(f"Unsupported command arguments: {vars(args)}")
        parser.print_help()
