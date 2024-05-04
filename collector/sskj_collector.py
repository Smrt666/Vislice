import requests
from bs4 import BeautifulSoup, Tag
from threading import Thread
from queue import Queue

url = "https://www.fran.si/iskanje"


def get_sskj_page(page: int, view: int = 1, query: str = "%2A") -> BeautifulSoup:
    # view 1 is ok, query "%2A" means "*" (all words)
    filtered_dictionary_ids: int = 130  # idk what this is
    params: dict[str, int | str] = {
        "View": view,
        "FilteredDictionaryIds": filtered_dictionary_ids,
        "Query": query,
        "Page": page,
    }
    response = requests.get(
        url,
        params=params,
    )
    response.raise_for_status()

    content = BeautifulSoup(response.content, features="html.parser")
    return content


def extract_words(content: BeautifulSoup) -> list[str]:
    word_paragraphs = content.find_all("div", class_="entry-content")
    words: list[str] = []
    for paragraph in word_paragraphs:
        # first <a href=...> child is the word
        word: str = paragraph.find("a").text
        words.append(word)
    return words


def get_all_words(
    lim: int | None = None, max_threads: int = 100, print_progress: bool = False
) -> list[str]:
    page1: BeautifulSoup = get_sskj_page(1)
    pagination = page1.find("ul", class_="pagination")
    assert isinstance(pagination, Tag), "Pagination not found on the first page."
    # the last li is "naslednja", the one before that is the last page
    last_page = int(pagination.find_all("li")[-2].text)

    if lim is not None:
        last_page = min(last_page, lim)

    words: list[str] = []
    threads: Queue[Thread] = Queue()
    if print_progress:
        print(f"Collecting words from {last_page} pages...")
    progress = 0
    for i in range(1, last_page + 1):
        while threads.qsize() >= max_threads:
            thread = threads.get()
            thread.join()
            progress += 1

        thread = Thread(target=lambda: words.extend(extract_words(get_sskj_page(i))))
        threads.put(thread)
        thread.start()

        if print_progress and progress % 13 == 1:  # 13 is a cool random number
            print(f"{progress}/{last_page} pages collected", end=" " * 10 + "\r")

    while not threads.empty():
        thread = threads.get()
        thread.join()
        progress += 1
        if print_progress and progress % 13 == 1:
            print(f"{progress}/{last_page} pages collected", end=" " * 10 + "\r")
    if print_progress:
        print(f"Finished collecting {progress} pages." + " " * 10)

    no_doubles = list(set(words))
    no_doubles.sort()

    return no_doubles


def sanitize(words: list[str]) -> list[str]:
    """Remove accents, words with special characters, ..."""
    alphabet = "abcčdefghijklmnoprsštuvzž"
    accents = {
        "í": "i",
        "ì": "i",
        "é": "e",
        "è": "e",
        "ê": "e",
        "á": "a",
        "à": "a",
        "ó": "o",
        "ò": "o",
        "ô": "o",
        "ú": "u",
        "ù": "u",
        "ŕ": "r",
        "ç": "c",
    }

    # remove accents and words with special characters
    tr = str.maketrans(accents | {k.upper(): v.upper() for k, v in accents.items()})
    words = [word.translate(tr) for word in words]

    # check problematic characters
    problems = [word for word in words if any(c not in alphabet for c in word.lower())]
    ok_problems = str.maketrans(
        {c: "" for c in " 0123456789-.,\"'xywqXYWQ" + alphabet + alphabet.upper()}
    )
    problems = [word for word in problems if word.translate(ok_problems).strip() != ""]
    if problems:
        print(f"Removing {len(problems)} words with special characters: {problems}")

    words = [word for word in words if all(c in alphabet for c in word.lower())]
    key_word = {(tuple(map(alphabet.index, word.lower())), word) for word in words}
    return [word for _, word in sorted(key_word)]
