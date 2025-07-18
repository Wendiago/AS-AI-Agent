import json, hashlib, os
from datetime import timezone, datetime
from pathlib import Path
from scraper_uploader.scraper import Scraper
from scraper_uploader.uploader import Uploader

HASH_FILE="hashes.json"
base_log_dir = os.environ.get("LOG_DIR", "logs")
scraping_log_dir = os.path.join(base_log_dir, "scraping")
upload_log_dir = os.path.join(base_log_dir, "upload")
data_dir = Path(os.environ.get("DATA_DIR", "data"))

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

def write_scraping_log(log_dir: str, added: int, updated: int, skipped: int):
    utc_now = datetime.now(timezone.utc)
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"{utc_now.date()}.json"
    log_file = os.path.join(log_dir, log_filename)

    # Load existing logs if file exists
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    # Append this run
    logs.append({
        "timestamp": utc_now.isoformat(),
        "added": added,
        "updated": updated,
        "skipped": skipped,
    })

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)
    
    print(f"\nScraping results: {added} added, {updated} updated, {skipped} skipped")
       
def run_job():
    # Initialize services
    scraper = Scraper()
    uploader = Uploader(
        vector_store_id=os.environ.get("VECTOR_STORE_ID"),
        vector_store_name=os.environ.get("VECTOR_STORE_NAME", "knowledge_base")
    )
    
    # Load existing hash if exists
    existing_hashes = load_hashes()
    new_hashes = {}
    added, updated, skipped = 0, 0, 0
    
    # Track changed files
    changed_files = []

    # 1. Re-scrape articles
    articles = scraper.fetch_articles()

    for article in articles:
        cleaned_content = scraper.clean_article_content(article.get("body", ""))
        article_id = scraper.extract_slug_from_url(article["html_url"])
        content_hash = calculate_hash(cleaned_content)
        new_hashes[article_id] = content_hash

        # 2. Detect changes and save files
        # If the scraped article is new, save it and added +1, if it's different, save and updated +1, else skipped +1
        if article_id not in existing_hashes:
            added += 1
            scraper.save_article(article, cleaned_content)
            changed_files.append(f"{article_id}.md")
        elif existing_hashes[article_id] != content_hash:
            updated += 1
            scraper.save_article(article, cleaned_content)
            changed_files.append(f"{article_id}.md")
        else:
            skipped += 1

    save_hashes(new_hashes)

    # Write log, add additional logging objects if run multiple times in a day
    # Log is named based on logging date
    write_scraping_log(scraping_log_dir, added, updated, skipped)
    
    print(f"Files to upload: {len(changed_files)}")
    
    # 3. Upload the change files
    if changed_files:
        print(f"\nSTEP 2: Uploading {len(changed_files)} changed files...")
        
        # Convert filenames to full paths
        files_to_upload = [data_dir / filename for filename in changed_files]
        
        # Upload the changed files
        uploader.upload_files_to_vector_store(files_to_upload)
        
        # Write upload log
        uploader.write_upload_log(
            uploaded_count=len(changed_files),
        )
    else:
        print("\nSTEP 2: No files to upload - all articles unchanged")
    
    # Final summary
    print("\n" + "=" * 60)
    print("DAILY JOB COMPLETE")
    print("=" * 60)
    print(f"Scraped: {added} new, {updated} updated, {skipped} unchanged")
    print(f"Uploaded: {len(changed_files)} files to vector store")
    print("=" * 60)
    
if __name__ == "__main__":
    run_job()