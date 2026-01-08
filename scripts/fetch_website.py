import os
import asyncio
import argparse
import re
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import BM25ContentFilter, PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

def sanitize_filename(name):
    """Remove or replace characters that are not allowed in filenames."""
    name = re.sub(r'https?://', '', name)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name

async def crawl_prune(url: str):
    """Crawl URL with PruningContentFilter - removes boilerplate, keeps all content."""
    prune_filter = PruningContentFilter(
        threshold=0.45,
        threshold_type="dynamic",
        min_word_threshold=5
    )

    md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)
    config = CrawlerRunConfig(markdown_generator=md_generator)

    try:
        async with AsyncWebCrawler() as crawler:
            print(f"Crawling {url} with prune filter")
            result = await crawler.arun(url=url, config=config)

            if result.success:
                print("✅ Successfully crawled page")
                return {
                    "url": url,
                    "filter": "prune",
                    "query": None,
                    "cache": "0",
                    "markdown": result.markdown.fit_markdown or "",
                    "success": True
                }
            else:
                print(f"❌ Crawl failed: {result.error_message}")
                return {
                    "url": url,
                    "filter": "prune",
                    "query": None,
                    "cache": "0",
                    "markdown": "",
                    "success": False
                }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "url": url,
            "filter": "prune",
            "query": None,
            "cache": "0",
            "markdown": "",
            "success": False
        }


async def crawl_bm25(url: str, query: str):
    """Crawl URL with BM25 content filtering - filters by keyword relevance."""
    bm25_filter = BM25ContentFilter(user_query=query)

    md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
    config = CrawlerRunConfig(markdown_generator=md_generator)

    try:
        async with AsyncWebCrawler() as crawler:
            print(f"Crawling {url} with BM25 filter, query: '{query}'")
            result = await crawler.arun(url=url, config=config)

            if result.success:
                print("✅ Successfully crawled page")
                return {
                    "url": url,
                    "filter": "bm25",
                    "query": query,
                    "cache": "0",
                    "markdown": result.markdown.fit_markdown or "",
                    "success": True
                }
            else:
                print(f"❌ Crawl failed: {result.error_message}")
                return {
                    "url": url,
                    "filter": "bm25",
                    "query": query,
                    "cache": "0",
                    "markdown": "",
                    "success": False
                }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "url": url,
            "filter": "bm25",
            "query": query,
            "cache": "0",
            "markdown": "",
            "success": False
        }

async def main():
    parser = argparse.ArgumentParser(
        description="Crawl a website with content filtering.",
        epilog="""
Examples:
  python3 %(prog)s https://example.com                    # Prune mode (default)
  python3 %(prog)s https://example.com "keyword"          # Prune mode with keyword in filename
  python3 %(prog)s https://example.com "keyword" --mode bm25  # BM25 mode
        """
    )
    parser.add_argument("url", type=str, help="URL to crawl")
    parser.add_argument("q", type=str, nargs="?", default=None,
                        help="Keyword (optional for prune, required for bm25)")
    parser.add_argument("--mode", type=str, choices=["prune", "bm25"], default="prune",
                        help="Filter mode: prune (default) or bm25")
    args = parser.parse_args()

    # Validate: BM25 requires keyword
    if args.mode == "bm25" and not args.q:
        parser.error("--mode bm25 requires a keyword argument")

    # Run appropriate crawler
    if args.mode == "prune":
        result = await crawl_prune(args.url)
    else:
        result = await crawl_bm25(args.url, args.q)

    # Save output
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tasks')
    os.makedirs(output_dir, exist_ok=True)

    sanitized_url = sanitize_filename(args.url)

    if args.q:
        sanitized_query = sanitize_filename(args.q.replace(" ", "_"))
        filename = f"{sanitized_url}:{sanitized_query}.json"
    else:
        filename = f"{sanitized_url}.json"

    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"Successfully saved output to {filepath}")

if __name__ == "__main__":
    asyncio.run(main())
