import json, hashlib, os
from datetime import timezone, datetime
from scraper_uploader.scraper import Scraper

HASH_FILE="hashes.json"
log_dir = os.environ.get("LOG_DIR") or "logs"

def load_hashes():
    """
    Load articles hash if exists
    """
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2)
        
def calculate_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def run_job():
    scraper = Scraper()
    existing_hashes = load_hashes()
    new_hashes = {}
    added, updated, skipped = 0, 0, 0

    articles = scraper.fetch_articles()

    for article in articles:
        cleaned_content = scraper.clean_article_content(article.get("body", ""))
        article_id = scraper.extract_slug_from_url(article["html_url"])
        content_hash = calculate_hash(cleaned_content)
        new_hashes[article_id] = content_hash

        # If the scraped article is new, save it and added +1, if it's different, save and updated +1, else skipped +1
        if article_id not in existing_hashes:
            added += 1
            scraper.save_article(article, cleaned_content)
        elif existing_hashes[article_id] != content_hash:
            updated += 1
            scraper.save_article(article, cleaned_content)
        else:
            skipped += 1

    save_hashes(new_hashes)

    # Write log for each day
    utc_now = datetime.now(timezone.utc)
    os.makedirs(log_dir, exist_ok=True)
    log_data = {
        "timestamp": utc_now.isoformat(),
        "added": added,
        "updated": updated,
        "skipped": skipped,
    }
    log_filename = os.path.join(log_dir, f"{utc_now.date()}.json")
    with open(log_filename, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)

    print(f"Job complete: {added} added, {updated} updated, {skipped} skipped.")
    print(f"Log written to {log_filename}")

if __name__ == "__main__":
    run_job()