import requests
from typing import Iterable
import re
import os

API_ENDPOINT = "https://github.com/Smrt666/Vislice.git/info/lfs/objects/batch"
lf_info_matcher = re.compile(
    r"version https://git-lfs.github.com/spec/v1\noid "
    r"(?P<hash_algo>[a-zA-Z0-9_\-\+]+):(?P<oid>[a-zA-Z0-9_\-+]+)\nsize (?P<size>\d+)\n"
)


def get_lf_info(file_path) -> None | dict[str, str]:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read(1024)  # 150 bytes should already be enough
    result = lf_info_matcher.fullmatch(content)
    if result is None:
        return None
    return result.groupdict()


def get_all_lf_data(directory_path) -> Iterable[tuple[str, dict[str, str] | None]]:
    for entry in os.scandir(directory_path):
        if entry.is_file():
            lf_info = get_lf_info(entry.path)
            yield entry.path, lf_info
        elif entry.is_dir():
            yield from get_all_lf_data(entry.path)


def download_lfs(lfs_info: list[dict[str, str]]) -> None:
    headers = {"Accept": "application/vnd.git-lfs+json", "Content-Type": "application/vnd.git-lfs+json; charset=utf-8"}

    hash_algos = {lf_info["hash_algo"] for lf_info in lfs_info}
    for hash_algo in hash_algos:
        data = {
            "operation": "download",
            "transfers": ["basic"],
            "objects": [
                {"oid": lf_info["oid"], "size": int(lf_info["size"])}
                for lf_info in lfs_info
                if lf_info["hash_algo"] == hash_algo
            ],
            "hash_algo": hash_algo,
        }

        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        if not response.ok or "objects" not in response.json():
            print(
                f"Failed to download LFS data: {response.text} objects: "
                f"{[lf_info for lf_info in lfs_info if lf_info["hash_algo"] == hash_algo]}"
            )
        hrefs = [obj["actions"]["download"].get("href", None) for obj in response.json()["objects"]]
        headerss = [obj["actions"]["download"].get("header", None) for obj in response.json()["objects"]]
        errors = [obj["actions"]["download"].get("error", None) for obj in response.json()["objects"]]
        files = [lf_info["file"] for lf_info in lfs_info if lf_info["hash_algo"] == hash_algo]
        for href, header, file_name, error in zip(hrefs, headerss, files, errors):
            try:
                if error is not None:
                    print(f"Failed to download LFS data for file {file_name}. Error: {error}")
                    continue
                res = requests.get(href, stream=True, headers=header)
                with open(file_name, "wb") as file:
                    for chunk in res.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(f"Downloaded file {file_name}.")
            except Exception as e:
                print(f"Failed to download file {file_name} from {href}: {e}")
    print("Finished downloading large files.")


def download_all_lfs(directory_path) -> None:
    lfs_info = [{"file": file_path, **lf_info} for file_path, lf_info in get_all_lf_data(directory_path) if lf_info is not None]
    download_lfs(lfs_info)


if __name__ == "__main__":
    download_all_lfs(os.path.dirname(__file__))
