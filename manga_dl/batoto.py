import argparse
import json
import os
import re
import shutil
from multiprocessing.pool import ThreadPool
from urllib.parse import urljoin
from zipfile import ZipFile

import js2py
import requests
from bs4 import BeautifulSoup

from manga_dl.aes import decrypt
from manga_dl.log import logger
from manga_dl.util import to_jpeg


class BotoScraper:

    def __init__(self, url, output):
        self._url = url
        self._session = requests.session()
        self._output = output

    def get_chapters(self):
        logger.debug("Getting chapters")

        r = self._session.get(self._url)
        soup = BeautifulSoup(r.content, "html.parser")

        urls = set()

        for anchor in soup.find_all("a", class_="visited chapt"):
            urls.add(urljoin(r.url, anchor.get("href")))

        return list(sorted(urls))

    def download_chapter(self, chapter_url):
        r = self._session.get(chapter_url)

        series_name = re.search(r"const local_text_sub = (.*);", r.text).group(1).strip("'")
        chapter_name = re.search(r"const local_text_epi = (.*);", r.text).group(1).strip("'")

        out_name = f"{series_name}_{chapter_name}.cbz"
        out_path = os.path.join(self._output, series_name, out_name)

        if os.path.exists(out_path):
            logger.debug(f"Skipping {out_path}")
            return

        # Remove DRM...
        img_list = json.loads(re.search(r"const imgHttpLis = (.*);", r.text).group(1))
        bato_pass = js2py.eval_js(re.search(r"const batoPass = (.*);", r.text).group(1))
        bato_word = re.search(r"const batoWord = (.*);", r.text).group(1).strip("\"")

        logger.debug(f"Breaking DRM, password={bato_pass} word={bato_word}")

        query_args = json.loads(decrypt(bato_word, bato_pass).decode())

        # Download images
        def dl_img(url):
            logger.info(f"GET {url}")
            img_bytes = self._session.get(url).content

            if ".webp" in url:
                img_bytes = to_jpeg(img_bytes)

            return img_bytes

        pool = ThreadPool(processes=10)
        image_urls = [f"{img}?{args}" for img, args in zip(img_list, query_args)]
        images = pool.map(dl_img, image_urls)

        # Create CBZ
        logger.info(f"Writing to {out_path}")

        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with ZipFile(out_path + ".part", mode="w") as archive:
            for i, img_bytes in enumerate(images):
                with archive.open(f"{i:04}.png", "w") as f:
                    f.write(img_bytes)

        shutil.move(out_path + ".part", out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download from bato.to")
    parser.add_argument("series_url", help="Series url https://bato.to/series/XXXXX")
    parser.add_argument("-o", "--output", help="Output folder", default=".")

    args = parser.parse_args()

    s = BotoScraper(args.series_url, args.output)
    for chapter in s.get_chapters():
        s.download_chapter(chapter)
