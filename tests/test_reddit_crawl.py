from unittest.mock import MagicMock, patch

import requests

from src.crawler.reddit_crawl import RedditCrawl
from src.entity.scrapped_link import LinkType


class TestRedditCrawl:

    @staticmethod
    def _makeRedditJson(posts: list[dict]) -> dict:
        return {
            "data": {
                "children": [{"kind": "t3", "data": post} for post in posts]
            }
        }

    @staticmethod
    def _makeTextPost(postId="abc", title="Title", selftext="Body text", subreddit="test") -> dict:
        return {
            "id": postId,
            "subreddit": subreddit,
            "title": title,
            "selftext": selftext,
            "url": f"https://www.reddit.com/r/{subreddit}/comments/{postId}",
            "permalink": f"/r/{subreddit}/comments/{postId}/slug/",
            "post_hint": "self",
        }

    @staticmethod
    def _makeImagePost(postId="img1", subreddit="pics") -> dict:
        return {
            "id": postId,
            "subreddit": subreddit,
            "title": "Cool picture",
            "selftext": "",
            "url": "https://i.redd.it/something.jpg",
            "permalink": f"/r/{subreddit}/comments/{postId}/slug/",
            "post_hint": "image",
        }

    @staticmethod
    def _makeVideoPost(postId="vid1", subreddit="videos") -> dict:
        return {
            "id": postId,
            "subreddit": subreddit,
            "title": "Cool video",
            "selftext": "",
            "url": "https://v.redd.it/something",
            "permalink": f"/r/{subreddit}/comments/{postId}/slug/",
            "is_video": True,
        }

    @staticmethod
    def _mockResponse(jsonData):
        resp = MagicMock()
        resp.json.return_value = jsonData
        resp.raise_for_status.return_value = None
        return resp

    @patch("src.crawler.reddit_crawl.time.sleep")
    @patch("src.crawler.reddit_crawl.requests.get")
    def test_crawl_returns_text_post(self, mockGet, mockSleep) -> None:
        mockGet.return_value = self._mockResponse(self._makeRedditJson([self._makeTextPost()]))

        results = RedditCrawl(["https://www.reddit.com/r/test"]).crawl()

        assert len(results) == 1
        assert results[0].linkType == LinkType.TEXT
        assert "Title" in results[0].data
        assert "Body text" in results[0].data

    @patch("src.crawler.reddit_crawl.time.sleep")
    @patch("src.crawler.reddit_crawl.requests.get")
    def test_crawl_returns_image_post(self, mockGet, mockSleep) -> None:
        mockGet.return_value = self._mockResponse(self._makeRedditJson([self._makeImagePost()]))

        results = RedditCrawl(["https://www.reddit.com/r/pics"]).crawl()

        assert len(results) == 1
        assert results[0].linkType == LinkType.PICTURES
        assert results[0].data.startswith("s3://reddit-scraper-bucket/")

    @patch("src.crawler.reddit_crawl.time.sleep")
    @patch("src.crawler.reddit_crawl.requests.get")
    def test_crawl_returns_video_post(self, mockGet, mockSleep) -> None:
        mockGet.return_value = self._mockResponse(self._makeRedditJson([self._makeVideoPost()]))

        results = RedditCrawl(["https://www.reddit.com/r/videos"]).crawl()

        assert len(results) == 1
        assert results[0].linkType == LinkType.VIDEO
        assert ".mp4" in results[0].data

    @patch("src.crawler.reddit_crawl.time.sleep")
    @patch("src.crawler.reddit_crawl.requests.get")
    def test_crawl_max_10_results(self, mockGet, mockSleep) -> None:
        posts = [self._makeTextPost(postId=f"p{i}") for i in range(15)]
        mockGet.return_value = self._mockResponse(self._makeRedditJson(posts))

        results = RedditCrawl(["https://www.reddit.com/r/test"]).crawl()

        assert len(results) == 10

    @patch("src.crawler.reddit_crawl.time.sleep")
    @patch("src.crawler.reddit_crawl.requests.get")
    def test_crawl_text_truncated_to_1025(self, mockGet, mockSleep) -> None:
        post = self._makeTextPost(selftext="x" * 2000)
        mockGet.return_value = self._mockResponse(self._makeRedditJson([post]))

        results = RedditCrawl(["https://www.reddit.com/r/test"]).crawl()

        assert len(results[0].data) <= 1025

    @patch("src.crawler.reddit_crawl.time.sleep")
    @patch("src.crawler.reddit_crawl.requests.get")
    def test_crawl_multiple_seeds(self, mockGet, mockSleep) -> None:
        resp1 = self._mockResponse(self._makeRedditJson([self._makeTextPost(postId="a")]))
        resp2 = self._mockResponse(self._makeRedditJson([self._makeImagePost(postId="b")]))
        mockGet.side_effect = [resp1, resp2]

        results = RedditCrawl([
            "https://www.reddit.com/r/test",
            "https://www.reddit.com/r/pics",
        ]).crawl()

        assert len(results) == 2
        assert results[0].linkType == LinkType.TEXT
        assert results[1].linkType == LinkType.PICTURES

    @patch("src.crawler.reddit_crawl.time.sleep")
    @patch("src.crawler.reddit_crawl.requests.get")
    def test_crawl_handles_http_error(self, mockGet, mockSleep) -> None:
        mockGet.side_effect = requests.RequestException("Connection failed")

        results = RedditCrawl(["https://www.reddit.com/r/nonexistent"]).crawl()

        assert results == []

    @patch("src.crawler.reddit_crawl.time.sleep")
    @patch("src.crawler.reddit_crawl.requests.get")
    def test_backpressure_sleep_called(self, mockGet, mockSleep) -> None:
        mockGet.return_value = self._mockResponse(self._makeRedditJson([self._makeTextPost()]))

        RedditCrawl(["https://www.reddit.com/r/a", "https://www.reddit.com/r/b"]).crawl()

        assert mockSleep.call_count == 2

    def test_to_json_url(self) -> None:
        assert RedditCrawl._toJsonUrl("https://www.reddit.com/r/test") == \
            "https://www.reddit.com/r/test.json"
        assert RedditCrawl._toJsonUrl("https://www.reddit.com/r/test/") == \
            "https://www.reddit.com/r/test.json"
        assert RedditCrawl._toJsonUrl("https://www.reddit.com/r/test.json") == \
            "https://www.reddit.com/r/test.json"

    @patch("src.crawler.reddit_crawl.time.sleep")
    @patch("src.crawler.reddit_crawl.requests.get")
    def test_crawl_empty_seed_list(self, mockGet, mockSleep) -> None:
        results = RedditCrawl([]).crawl()

        assert results == []
        mockGet.assert_not_called()
