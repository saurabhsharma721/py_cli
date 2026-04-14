import time

import requests

from src.crawler.crawl import Crawl
from src.entity.scrapped_link import LinkType, ScrappedLink


class RedditCrawl(Crawl):

    USER_AGENT: str = "py-cli-reddit-crawler/0.1"

    def __init__(self, seedUrls: list[str], maxResults: int = 10,
                 requestDelay: float = 1.0, textMaxLength: int = 1025) -> None:
        self._seedUrls = seedUrls
        self._maxResults = maxResults
        self._requestDelay = requestDelay
        self._textMaxLength = textMaxLength
        self._results: list[ScrappedLink] = []

    def crawl(self) -> list[ScrappedLink]:
        self._results = []
        for seedUrl in self._seedUrls:
            if len(self._results) >= self._maxResults:
                break
            self._crawlSeed(seedUrl)
        return self._results

    def _crawlSeed(self, url: str) -> None:
        jsonUrl = self._toJsonUrl(url)
        response = self._fetch(jsonUrl)
        if response is None:
            return
        posts = self._extractPosts(response)
        for post in posts:
            if len(self._results) >= self._maxResults:
                break
            link = self._processPost(post)
            if link is not None:
                self._results.append(link)

    def _fetch(self, url: str) -> dict | None:
        time.sleep(self._requestDelay)
        try:
            resp = requests.get(url, headers={"User-Agent": self.USER_AGENT}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError):
            return None

    def _extractPosts(self, jsonData: dict) -> list[dict]:
        if isinstance(jsonData, list):
            children = jsonData[0].get("data", {}).get("children", [])
        else:
            children = jsonData.get("data", {}).get("children", [])
        return [child.get("data", {}) for child in children if child.get("kind") == "t3"]

    def _classifyPost(self, post: dict) -> LinkType:
        if post.get("is_video", False):
            return LinkType.VIDEO
        postHint = post.get("post_hint", "")
        if postHint in ("hosted:video", "rich:video"):
            return LinkType.VIDEO
        if postHint == "image":
            return LinkType.PICTURES
        url = post.get("url", "")
        if any(url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp")):
            return LinkType.PICTURES
        return LinkType.TEXT

    def _processPost(self, post: dict) -> ScrappedLink | None:
        url = post.get("url", "")
        permalink = post.get("permalink", "")
        postId = post.get("id", "unknown")
        subreddit = post.get("subreddit", "unknown")
        if not url:
            return None

        linkType = self._classifyPost(post)

        if linkType == LinkType.TEXT:
            title = post.get("title", "")
            selftext = post.get("selftext", "")
            text = f"{title}\n\n{selftext}".strip()
            data = text[: self._textMaxLength]
        elif linkType == LinkType.VIDEO:
            data = f"s3://reddit-scraper-bucket/{subreddit}/{postId}.mp4"
        else:
            ext = url.rsplit(".", 1)[-1] if "." in url else "jpg"
            data = f"s3://reddit-scraper-bucket/{subreddit}/{postId}.{ext}"

        fullUrl = f"https://www.reddit.com{permalink}" if permalink else url
        return ScrappedLink(url=fullUrl, linkType=linkType, data=data)

    @staticmethod
    def _toJsonUrl(url: str) -> str:
        url = url.rstrip("/")
        if not url.endswith(".json"):
            url += ".json"
        return url
