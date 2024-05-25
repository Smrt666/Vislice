# type: ignore
# https://www.google.com/search?as_q=&as_epq=avtocesta&as_oq=&as_eq=&as_nlo=&as_nhi=&lr=lang_sl&cr=&as_qdr=all&as_sitesearch=&as_occt=any&as_filetype=&tbs=
import requests
from bs4 import BeautifulSoup
import re
from collector.utils import multirun
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from contextlib import contextmanager


stat_num = re.compile(r"[1-9]+\d*(\.\d{3})*")


@contextmanager
def googler():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # if something goes wrong, change to 0 and good luck

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://google.com")

        sleep(1)
        # Set correct user agent
        btn = driver.find_elements("xpath", "//*[contains(text(), 'Sprejmi vse')]")
        if not btn:
            btn = driver.find_elements("xpath", "//*[contains(text(), 'Accept all')]")
        btn = btn[0]
        btn.click()

        selenium_user_agent = driver.execute_script("return navigator.userAgent;")
        s = requests.Session()
        s.headers.update({"user-agent": selenium_user_agent})

        for cookie in driver.get_cookies():
            s.cookies.set(cookie["name"], cookie["value"], domain=cookie["domain"])

        yield s
    finally:
        driver.quit()


def count_search_results(session, word: str, lang: str = "sl") -> int:
    params = {
        "as_q": "",
        "as_epq": word,
        "as_oq": "",
        "as_eq": "",
        "as_nlo": "",
        "as_nhi": "",
        "lr": f"lang_{lang}",
        "cr": "",
        "as_qdr": "all",
        "as_sitesearch": "",
        "as_occt": "any",
        "as_filetype": "",
        "tbs": "",
    }
    response = session.get(
        "https://www.google.com/search",
        params=params,
    )
    response.raise_for_status()

    content = BeautifulSoup(response.content, features="html.parser")
    print(content.prettify(), file=open("test.html", "w", encoding="UTF-8"))
    result_stats = content.find("div", id="result-stats")
    assert result_stats is not None, f"Result stats not found for word '{word}'."
    num = stat_num.search(result_stats.text)
    assert num is not None, f"Number not found in result stats for word '{word}'."
    num = result_stats.text[num.start() : num.end()]
    num = num.replace(".", "")
    return int(num)


def words_usage(words: list[str], lang: str = "sl", threads: int = 100, print_progress: bool = True) -> dict[str, int]:
    with googler() as session:
        usage = {}
        jobs = [lambda word=word: usage.update({word: count_search_results(session, word, lang)}) for word in words]
        if print_progress:
            progress_printer = lambda progress: print(f"{progress}/{len(words)} words counted", end=" " * 10 + "\r")  # noqa: E731
        multirun(jobs, threads, print_progress=progress_printer)
        return usage
