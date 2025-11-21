"""
Script to crawl documentation pages by following navigation links using LLM.

This script starts from a base documentation URL and uses GPT-5.1 (via OpenAI API)
to identify and follow "next page" links throughout the documentation, building a complete
list of all pages in the documentation.

Usage:
    python crawl_documentation.py
    
Requirements:
    - OPENAI_API_KEY environment variable set in .env file
"""

import requests
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION - Modify these variables to customize the crawler
# ============================================================================

# OpenAI API key (loaded from .env file)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file")

# Model configuration
MODEL_NAME = "gpt-5.1"  # Model to use for link extraction
REASONING_EFFORT = "high"  # Reasoning effort level: "low", "medium", or "high"

# Crawler configuration
MAX_PAGES = 200  # Maximum number of pages to crawl (safety limit)
DELAY_BETWEEN_PAGES = 2  # Seconds to wait between page requests

# ============================================================================


def download_html(url: str) -> Optional[str]:
    """
    Download HTML content from a given URL.
    
    Args:
        url (str): The URL to download HTML from.
        
    Returns:
        Optional[str]: The HTML content as a string, or None if download fails.
    """
    try:
        print(f"📥 Downloading: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"❌ Error downloading {url}: {e}")
        return None


def extract_next_link(html: str, current_url: str, llm: ChatOpenAI) -> Optional[str]:
    """
    Use LLM to extract the next documentation page link from HTML content.
    
    Args:
        html (str): The HTML content to analyze.
        current_url (str): The current page URL (for constructing absolute URLs).
        llm (ChatOpenAI): The language model instance to use for extraction.
        
    Returns:
        Optional[str]: The next page URL, or None if no next link is found.
    """
    # Truncate HTML if too long (keep first and last parts where nav links usually are)
    max_chars = 30000
    if len(html) > max_chars:
        html_start = html[:15000]
        html_end = html[-15000:]
        truncated_html = html_start + "\n\n[... middle content truncated ...]\n\n" + html_end
    else:
        truncated_html = html
    
    # Create a clear system prompt for GPT-5.1 with high reasoning
    system_prompt = SystemMessage(content="""You are an expert at analyzing documentation HTML to find navigation links.

TASK: Find the link to the NEXT page in a sequential documentation.

CRITICAL RULES:
1. Look for links that navigate FORWARD in the documentation (not backward/previous)
2. Common patterns: arrows (→), "Next", page titles that indicate progression
3. Return the href value EXACTLY as written in the HTML - copy it character-by-character
4. Do NOT interpret, modify, fix, or normalize the href
5. If no next link exists, return exactly: NO_NEXT_LINK

WHAT TO LOOK FOR:
- Navigation bars (top/bottom of page)
- Sidebar navigation
- Inline "next page" links
- Links with arrows pointing right (→)
- Links labeled "Next", "Continue", or showing the next topic name

OUTPUT FORMAT:
Return ONLY the href value, nothing else.

EXAMPLES:
<a href="/main/guides/the-interface-class">The Interface Class →</a>
→ Output: /main/guides/the-interface-class

<a href="../more-examples/">More Examples</a>  
→ Output: ../more-examples/

<a href="https://example.com/docs/next">Next</a>
→ Output: https://example.com/docs/next

No next link present
→ Output: NO_NEXT_LINK""")
    
    # Create the user prompt with the HTML
    user_prompt = HumanMessage(content=f"""Here is the HTML from the current documentation page:

{truncated_html}

What is the href of the NEXT page link? Return only the URL path or "NO_NEXT_LINK".""")
    
    print("🤖 Asking GPT-5.1 to find next link...")
    
    # Retry logic for rate limits
    max_retries = 3
    retry_delay = 3  # seconds
    
    for attempt in range(max_retries):
        try:
            # Use ChatOpenAI API
            response = llm.invoke([system_prompt, user_prompt])
            answer = response.content.strip()
            
            print(f"💭 LLM response: {answer}")
            
            # Check if no next link was found
            if "NO_NEXT_LINK" in answer.upper():
                return None
            
            # Clean up the response (remove quotes, extra whitespace)
            answer = answer.strip('"').strip("'").strip()
            
            # If the answer looks like a URL or path, process it
            if answer:
                # Use urljoin to handle all types of URLs (absolute, relative, with .., etc.)
                absolute_url = urljoin(current_url, answer)
                
                # Normalize URL to remove duplicate path segments (e.g., /guides/guides/ -> /guides/)
                from urllib.parse import urlparse, urlunparse
                parsed = urlparse(absolute_url)
                path_parts = parsed.path.split('/')
                
                # Remove duplicate consecutive directory names
                normalized_parts = []
                for part in path_parts:
                    if not normalized_parts or normalized_parts[-1] != part or part == '':
                        normalized_parts.append(part)
                
                normalized_path = '/'.join(normalized_parts)
                normalized_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    normalized_path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                
                print(f"🔗 Original: {absolute_url}")
                if normalized_url != absolute_url:
                    print(f"🔧 Normalized: {normalized_url}")
                
                return normalized_url
            
            return None
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a rate limit error
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"⏳ Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Rate limit exceeded after {max_retries} retries")
                    return None
            else:
                print(f"❌ Error calling LLM: {e}")
                return None
    
    return None


def crawl_documentation(start_url: str, max_pages: int = None) -> List[str]:
    """
    Crawl documentation pages starting from a base URL.
    
    This function uses an LLM via OpenAI to intelligently follow "next page" links
    throughout the documentation, building a complete list of pages.
    
    Args:
        start_url (str): The starting URL of the documentation.
        max_pages (int, optional): Maximum number of pages to crawl. If None, uses global MAX_PAGES.
        
    Returns:
        List[str]: A list of all documentation page URLs found.
    """
    # Use global max_pages if not specified
    if max_pages is None:
        max_pages = MAX_PAGES
    
    # Initialize the LLM with configured model and reasoning effort
    print(f"🚀 Initializing {MODEL_NAME} via OpenAI with {REASONING_EFFORT} reasoning effort...")
    llm = ChatOpenAI(
        model=MODEL_NAME,
        # Note: temperature is not configurable with reasoning models (uses default 1.0)
        api_key=OPENAI_API_KEY,
        model_kwargs={
            "reasoning_effort": REASONING_EFFORT,
        }
    )
    print("✅ LLM ready\n")
    
    # Keep track of visited URLs to avoid loops
    visited_urls = []
    current_url = start_url
    
    print(f"📚 Starting documentation crawl from: {start_url}")
    print(f"⚠️  Maximum pages to crawl: {max_pages}\n")
    print("=" * 80)
    
    while current_url and len(visited_urls) < max_pages:
        # Check if we've already visited this URL
        if current_url in visited_urls:
            print(f"🔄 Already visited {current_url}, stopping to avoid loop")
            break
        
        # Add current URL to visited list
        visited_urls.append(current_url)
        print(f"\n📄 Page {len(visited_urls)}: {current_url}")
        
        # Download the HTML
        html = download_html(current_url)
        if not html:
            print("❌ Failed to download HTML, stopping crawl")
            break
        
        # Extract the next link using LLM
        next_url = extract_next_link(html, current_url, llm)
        
        if next_url:
            print(f"✅ Found next link: {next_url}")
            current_url = next_url
            # Small delay to be respectful to the server and avoid rate limits
            time.sleep(DELAY_BETWEEN_PAGES)
        else:
            print("🏁 No more pages found, crawl complete!")
            break
        
        print("-" * 80)
    
    if len(visited_urls) >= max_pages:
        print(f"\n⚠️  Reached maximum page limit ({max_pages})")
    
    print("\n" + "=" * 80)
    print(f"✨ Crawl complete! Found {len(visited_urls)} pages\n")
    
    return visited_urls


def main():
    """
    Main function to run the documentation crawler.
    """
    # Example: Gradio documentation
    start_url = "https://www.gradio.app/main/guides/quickstart"
    
    print("🔍 Documentation Crawler")
    print("=" * 80)
    print(f"Starting URL: {start_url}")
    print(f"Model: {MODEL_NAME} (reasoning: {REASONING_EFFORT})")
    print(f"Max pages: {MAX_PAGES}\n")
    
    # Crawl the documentation
    all_urls = crawl_documentation(start_url)
    
    # Display results
    print("\n📋 Complete list of documentation pages:")
    print("=" * 80)
    for i, url in enumerate(all_urls, 1):
        print(f"{i:2d}. {url}")
    
    # Save to file
    output_file = "documentation_urls.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in all_urls:
            f.write(f"{url}\n")
    
    print(f"\n💾 URLs saved to: {output_file}")


if __name__ == "__main__":
    main()

