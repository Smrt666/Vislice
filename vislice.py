import argparse

from collector.sskj_collector import get_all_words, sanitize

parser = argparse.ArgumentParser(description="Script for this project.")
subparsers = parser.add_subparsers(help="sub-command help", dest="action")

# sskjcollect
sskjcollect_parser = subparsers.add_parser(
    "sskjcollect", help="collect words from SSKJ"
)
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
    case _:
        print(f"Unsupported command arguments: {vars(args)}")
