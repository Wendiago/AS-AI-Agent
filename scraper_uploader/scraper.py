import os
import requests
import re
from html2text import HTML2Text
from pathlib import Path
from urllib.parse import urlparse
from common.env_config import config

class Scraper:    
    def __init__(self) -> None:
        self.limit = config.SCRAPING_LIMIT
        self.subdomain = config.SCRAPING_SOURCE_SUBDOMAIN
        self.output_dir = config.DATA_DIR
        self.session = requests.Session()
        
    @property
    def base_url(self) -> str:
        """Zendesk url for fetching articles."""
        return f"https://support.{self.subdomain}.com/api/v2/help_center/en-us/articles.json?per_page={self.limit}"
    
    def fetch_articles(self):
        """
        Fetch up to SCRAPING_LIMIT number of articles
        """
        print(f"Fetching first {self.limit} articles from: {self.base_url}")
        res = self.session.get(self.base_url)
        res.raise_for_status()
        return res.json().get("articles", [])
            
    def extract_slug_from_url(self, html_url: str) -> str:
        """
        Extract the last part of the html_url to use as a slug.
        Example:
        'https://support.optisigns.com/hc/en-us/articles/42915219118739-Legacy-DataSources'
        -> '42915219118739-Legacy-DataSources'
        """
        path = urlparse(html_url).path
        return path.rstrip("/").split("/")[-1]
    
    def clean_article_content(self, html: str) -> str:
        """
        Convert HTML content to Markdown, removing nav/ads but keeping links, code blocks, and headings.
        """
        
        # Common patterns for nav and ads
        html = re.sub(r'<nav.*?</nav>', '', html, flags=re.DOTALL)
        html = re.sub(r'<aside.*?</aside>', '', html, flags=re.DOTALL)

        converter = HTML2Text()
        converter.ignore_links = False
        converter.body_width = 0 
        converter.ignore_images = False
        converter.ignore_emphasis = False

        md = converter.handle(html)
        md = re.sub(r'\n{3,}', '\n\n', md).strip()
        return md
            
    def save_article(self, article, cleaned_article_content=None):
        """
        Convert article JSON to Markdown and save as <slug>.md.
        """
        body_html = article.get("body", "")
        html_url = article.get("html_url", "")

        slug = self.extract_slug_from_url(html_url)
        filename = self.output_dir / f"{slug}.md"

        if (cleaned_article_content is not None):
            filename.write_text(cleaned_article_content, encoding="utf-8")
        else:
            md_content = self.clean_article_content(body_html)
            filename.write_text(md_content, encoding="utf-8")

        print(f"Saved: {filename}")
        
if __name__ == "__main__":
    scraper = Scraper()
    scraper.fetch_articles()