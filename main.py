"""
Main script to crawl documentation and convert all pages to Markdown.

This script orchestrates the entire process:
1. Crawls a documentation website to find all pages (URLs saved by crawler)
2. Reads URLs from the file created by the crawler
3. Converts each page to Markdown format
4. Saves all Markdown files in an organized output directory

Usage:
    python main.py <base_url> [-o OUTPUT_DIR] [-f URLS_FILE]

Examples:
    python main.py "https://www.gradio.app/main/guides/quickstart"
    python main.py "https://docs.python.org/3/tutorial/" -o python_docs
    python main.py "https://example.com/docs" -o docs -f urls.txt
"""

import sys
import argparse
from pathlib import Path
from urllib.parse import urlparse
import re

# Import functions from our other scripts
from crawl_documentation import crawl_documentation
from url_to_markdown import convert_url_to_markdown


def sanitize_filename(url: str) -> str:
    """
    Convert a URL to a safe filename for saving Markdown files.
    
    Args:
        url (str): The URL to convert to a filename
        
    Returns:
        str: A sanitized filename safe for all operating systems
        
    Example:
        "https://example.com/docs/getting-started" -> "docs_getting-started.md"
    """
    # Parse the URL to get the path component
    parsed = urlparse(url)
    path = parsed.path
    
    # Remove leading/trailing slashes
    path = path.strip('/')
    
    # Replace slashes with underscores
    path = path.replace('/', '_')
    
    # Remove or replace unsafe characters for filenames
    # Keep only alphanumeric, dash, underscore, and dots
    path = re.sub(r'[^\w\-_\.]', '_', path)
    
    # Remove consecutive underscores
    path = re.sub(r'_+', '_', path)
    
    # If the path is empty, use the domain name
    if not path:
        path = parsed.netloc.replace('.', '_')
    
    # Add .md extension
    return f"{path}.md"


def process_documentation(base_url: str, output_dir: str = "markdown_output", urls_file: str = "documentation_urls.txt") -> None:
    """
    Main processing function that crawls documentation and converts to Markdown.
    
    This function:
    1. Crawls the documentation starting from base_url (URLs are saved automatically by crawler)
    2. Reads URLs from the file created by the crawler
    3. Creates an output directory for Markdown files
    4. Converts each URL to Markdown
    5. Saves files with descriptive names
    
    Args:
        base_url (str): The starting URL of the documentation to crawl
        output_dir (str): Directory where Markdown files will be saved (default: "markdown_output")
        urls_file (str): File where crawler saves URLs (default: "documentation_urls.txt")
    """
    print("\n" + "=" * 80)
    print("📚 ALL-TO-MARKDOWN - Documentation Converter")
    print("=" * 80)
    print(f"🌐 Base URL: {base_url}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 URLs file: {urls_file}\n")
    
    # Step 1: Crawl the documentation to get all URLs
    # Note: crawl_documentation() also saves URLs to the file automatically
    print("🔍 STEP 1: Crawling documentation to find all pages...")
    print("-" * 80)
    # crawl_documentation(base_url)
    print()  # Empty line for separation
    
    # Step 2: Read URLs from the file created by crawl_documentation()
    print("📖 STEP 2: Reading URLs from file...")
    print("-" * 80)
    urls_path = Path(urls_file)
    
    # Check if file exists
    if not urls_path.exists():
        print(f"❌ Error: URLs file not found: {urls_path.absolute()}")
        print("   The crawler should have created this file.")
        return
    
    # Read URLs from file
    try:
        with open(urls_path, 'r', encoding='utf-8') as f:
            # Read all lines and remove whitespace/newlines
            urls_to_convert = [line.strip() for line in f if line.strip()]
        print(f"✅ Read {len(urls_to_convert)} URLs from: {urls_path.absolute()}\n")
    except Exception as e:
        print(f"❌ Error reading URLs from file: {e}")
        return
    
    # Validate that we have URLs to convert
    if not urls_to_convert:
        print("❌ No URLs found in file. Exiting.")
        return
    
    # Step 3: Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print("📁 STEP 3: Creating output directory...")
    print("-" * 80)
    print(f"✅ Created directory: {output_path.absolute()}\n")
    
    # Step 4: Convert each URL to Markdown
    print("=" * 80)
    print("🔄 STEP 4: Converting pages to Markdown...")
    print("=" * 80 + "\n")
    
    successful_conversions = 0
    failed_conversions = 0
    
    for index, url in enumerate(urls_to_convert, 1):
        print(f"\n[{index}/{len(urls_to_convert)}] Processing: {url}")
        print("-" * 80)
        
        # Generate a unique filename for this URL
        filename = sanitize_filename(url)
        output_file = output_path / filename
        
        # Convert URL to Markdown
        success = convert_url_to_markdown(url, str(output_file))
        
        if success:
            successful_conversions += 1
            print(f"✅ Saved as: {filename}")
        else:
            failed_conversions += 1
            print(f"❌ Failed to convert: {url}")
        
        # Add a separator for readability
        if index < len(urls_to_convert):
            print()
    
    # Step 5: Display summary
    print("\n" + "=" * 80)
    print("✨ CONVERSION COMPLETE!")
    print("=" * 80)
    print(f"✅ Successfully converted: {successful_conversions} pages")
    if failed_conversions > 0:
        print(f"❌ Failed conversions: {failed_conversions} pages")
    print(f"📁 All files saved in: {output_path.absolute()}")
    print(f"💾 Total files created: {successful_conversions}")
    print("=" * 80 + "\n")


def main():
    """
    Main function for command-line execution.
    Parses arguments and starts the documentation conversion process.
    """
    # Create argument parser with detailed help
    parser = argparse.ArgumentParser(
        description="Crawl documentation website and convert all pages to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "https://www.gradio.app/main/guides/quickstart"
  python main.py "https://docs.python.org/3/tutorial/" -o python_docs
  python main.py "https://example.com/docs" -o docs -f urls.txt
  
This script will:
  1. Crawl the documentation starting from the base URL
  2. Read URLs from the file created by the crawler
  3. Convert each page to Markdown format
  4. Save all files in an organized output directory
  
Note: The crawler automatically saves URLs to documentation_urls.txt (or specified file)
      for reference and potential manual editing before conversion.
        """
    )
    
    # Add required positional argument
    parser.add_argument(
        "base_url",
        type=str,
        help="Base URL of the documentation to crawl and convert"
    )
    
    # Add optional arguments
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="markdown_output",
        help="Output directory for Markdown files (default: markdown_output)"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        default="documentation_urls.txt",
        help="File where crawler saves URLs and we read from (default: documentation_urls.txt)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    # Validate URL format
    if not (args.base_url.startswith("http://") or args.base_url.startswith("https://")):
        print("❌ Error: URL must start with 'http://' or 'https://'", file=sys.stderr)
        print(f"   Received: {args.base_url}")
        sys.exit(1)
    
    # Start the processing
    try:
        process_documentation(args.base_url, args.output, args.file)
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
