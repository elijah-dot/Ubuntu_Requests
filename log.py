import requests
import os
from urllib.parse import urlparse
import hashlib

def get_filename_from_url(url):
    """Extract filename from URL or generate a default one."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename or '.' not in filename:
        filename = "downloaded_image.jpg"
    return filename

def file_hash(filepath):
    """Calculate SHA256 hash of a file to detect duplicates."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def content_hash(content):
    """Calculate SHA256 hash of bytes content."""
    sha256 = hashlib.sha256()
    sha256.update(content)
    return sha256.hexdigest()

def sanitize_filename(filename):
    """Remove or replace characters that are invalid in filenames."""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")

    # Create directory if it doesn't exist
    os.makedirs("Fetched_Images", exist_ok=True)

    # Prompt user for one or multiple URLs separated by commas
    urls_input = input("Please enter one or more image URLs (comma separated): ")
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]

    # Keep track of hashes of already downloaded images to prevent duplicates
    existing_hashes = set()
    # Preload existing image hashes in the folder
    for existing_file in os.listdir("Fetched_Images"):
        path = os.path.join("Fetched_Images", existing_file)
        h = file_hash(path)
        if h:
            existing_hashes.add(h)

    for url in urls:
        try:
            # Fetch the image with a timeout and headers
            headers = {
                "User -Agent": "UbuntuImageFetcher/1.0 (+https://github.com/yourusername/Ubuntu_Requests)"
            }
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()

            # Check content-type header to ensure it's an image
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"✗ Skipping URL (not an image): {url}")
                continue

            # Calculate hash of content to detect duplicates
            img_hash = content_hash(response.content)
            if img_hash in existing_hashes:
                print(f"✗ Duplicate image detected, skipping download: {url}")
                continue

            # Extract and sanitize filename
            filename = get_filename_from_url(url)
            filename = sanitize_filename(filename)

            # If filename exists, append a number to avoid overwriting
            base, ext = os.path.splitext(filename)
            counter = 1
            filepath = os.path.join("Fetched_Images", filename)
            while os.path.exists(filepath):
                filepath = os.path.join("Fetched_Images", f"{base}_{counter}{ext}")
                counter += 1

            # Save the image in binary mode
            with open(filepath, 'wb') as f:
                f.write(response.content)

            # Add hash to existing hashes set
            existing_hashes.add(img_hash)

            print(f"✓ Successfully fetched: {os.path.basename(filepath)}")
            print(f"✓ Image saved to {filepath}")

        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error for URL {url}: {e}")
        except Exception as e:
            print(f"✗ An error occurred for URL {url}: {e}")

    print("\nConnection strengthened. Community enriched.")

if __name__ == "__main__":
    main()
# log.py