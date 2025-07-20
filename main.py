import os
from scraper_uploader.scraper import Scraper
from scraper_uploader.uploader import Uploader
from common.env_config import config
from utils.hash_util import HashUtil
       
def run_job():
    # Initialize services
    scraper = Scraper()
    uploader = Uploader(
        vector_store_id=os.environ.get("VECTOR_STORE_ID"),
        vector_store_name=os.environ.get("VECTOR_STORE_NAME", "knowledge_base")
    )
    
    # Load existing hash if exists
    existing_hashes = HashUtil.load_hashes()
    new_hashes = {}
    added, updated, skipped = 0, 0, 0
    
    # Track changed files
    changed_files = []

    # 1. Re-scrape articles
    print(f"\nSTEP 1: Scrape articles")
    articles = scraper.fetch_articles()

    for article in articles:
        cleaned_content = scraper.clean_article_content(article.get("body", ""))
        article_id = scraper.extract_slug_from_url(article["html_url"])
        content_hash = HashUtil.calculate_hash(cleaned_content)
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

    HashUtil.save_hashes(new_hashes)

    # Write log, add additional logging objects if run multiple times in a day
    # Log file is named based on logging date
    scraper.write_scraping_log(added, updated, skipped)
    
    print(f"Files to upload: {len(changed_files)}")
    
    # 3. Upload the change files
    if changed_files:
        print(f"\nSTEP 2: Uploading {len(changed_files)} changed files...")
        
        # Convert filenames to full paths
        files_to_upload = [config.DATA_DIR / filename for filename in changed_files]
        
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