"""CLI entry point using cyclopts."""

from __future__ import annotations

import cyclopts

from src.crawler.reddit_crawl import RedditCrawl

app = cyclopts.App(
    name="py-cli",
    help="Reddit crawler CLI.",
)


@app.default
def crawl(seeds: list[str] = ["https://www.reddit.com/r/programming/"]) -> None:
    """Crawl Reddit URLs and print scraped links.

    Args:
        seeds: Reddit URLs to crawl.
    """
    crawler = RedditCrawl(seeds)
    results = crawler.crawl()
    for i, link in enumerate(results, 1):
        print(f"[{i}] {link.linkType.value} | {link.url}")
        print(f"    {link.data[:80]}{'...' if len(link.data) > 80 else ''}")
        print()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
