"""
Microsoft Purview Sensitive Information Type (SIT) GUID Extractor
------------------------------------------------------------------
This script extracts SIT names and their corresponding GUIDs from Microsoft's
official documentation and creates an Excel mapping file.

Author: Generated for Purview eDiscovery GUID mapping
Date: 2026-03-31
"""

import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time

# Base URL for Microsoft Learn documentation
BASE_URL = "https://learn.microsoft.com"
MAIN_PAGE_URL = "https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-entity-definitions"

def fetch_page(url, max_retries=3):
    """Fetch a web page with retry logic"""
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed to fetch {url}: {e}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

def extract_sit_links(main_page_html):
    """Extract all SIT definition page links from the main listing page"""
    soup = BeautifulSoup(main_page_html, 'html.parser')
    
    # Find all links in the main content area
    links = []
    
    # Look for links that match the pattern for SIT definitions
    for link in soup.find_all('a', href=True):
        href = link['href']
        # SIT definition pages follow the pattern: /purview/sit-defn-*
        if '/purview/sit-defn-' in href:
            full_url = urljoin(BASE_URL, href)
            sit_name = link.get_text(strip=True)
            if sit_name:  # Only add if there's actual text
                links.append({
                    'name': sit_name,
                    'url': full_url
                })
    
    # Remove duplicates (same URL might appear multiple times)
    unique_links = {}
    for item in links:
        unique_links[item['url']] = item['name']
    
    return [{'name': name, 'url': url} for url, name in unique_links.items()]

def extract_guid_from_page(page_html):
    """Extract the GUID from a SIT definition page"""
    if not page_html:
        return None
    
    # Look for the Entity id pattern in the XML code block
    # Pattern: <Entity id="GUID-HERE" ...>
    guid_pattern = r'<Entity\s+id="([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})"'
    
    match = re.search(guid_pattern, page_html, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None

def main():
    print("=" * 70)
    print("Microsoft Purview SIT GUID Extraction Tool")
    print("=" * 70)
    print()
    
    # Step 1: Fetch the main documentation page
    print("Step 1: Fetching main SIT documentation page...")
    main_page_html = fetch_page(MAIN_PAGE_URL)
    
    if not main_page_html:
        print("ERROR: Could not fetch the main documentation page.")
        return
    
    print("✓ Main page fetched successfully")
    print()
    
    # Step 2: Extract all SIT definition links
    print("Step 2: Extracting SIT definition links...")
    sit_links = extract_sit_links(main_page_html)
    
    print(f"✓ Found {len(sit_links)} Sensitive Information Types")
    print()
    
    # Step 3: Fetch each SIT page and extract GUID
    print("Step 3: Extracting GUIDs from each SIT page...")
    print("(This may take a few minutes...)")
    print()
    
    results = []
    failed_extractions = []
    
    for idx, sit in enumerate(sit_links, 1):
        print(f"  [{idx}/{len(sit_links)}] Processing: {sit['name'][:50]}...", end=' ')
        
        # Fetch the individual SIT page
        page_html = fetch_page(sit['url'])
        
        if page_html:
            # Extract GUID
            guid = extract_guid_from_page(page_html)
            
            if guid:
                results.append({
                    'Classification_Name': sit['name'],
                    'GUID': guid,
                    'Documentation_URL': sit['url']
                })
                print("✓")
            else:
                failed_extractions.append(sit['name'])
                print("✗ (No GUID found)")
        else:
            failed_extractions.append(sit['name'])
            print("✗ (Page fetch failed)")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.5)
    
    print()
    print("=" * 70)
    print(f"Extraction Complete!")
    print(f"  - Successfully extracted: {len(results)} GUIDs")
    print(f"  - Failed extractions: {len(failed_extractions)}")
    print("=" * 70)
    print()
    
    # Step 4: Create DataFrame and export to Excel
    if results:
        df = pd.DataFrame(results)
        
        # Sort by Classification Name for easier lookup
        df = df.sort_values('Classification_Name').reset_index(drop=True)
        
        # Export to Excel
        output_file = '/mnt/user-data/outputs/Purview_SIT_Master_Mapping.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='SIT_GUID_Mapping', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['SIT_GUID_Mapping']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        print(f"✓ Excel file created: {output_file}")
        print()
        print("File contains 3 columns:")
        print("  1. Classification_Name - The SIT display name")
        print("  2. GUID - The unique identifier")
        print("  3. Documentation_URL - Link to Microsoft's documentation")
        print()
        
        # Show sample
        print("Sample entries:")
        print(df.head(5).to_string(index=False))
        print()
        
        if failed_extractions:
            print(f"Note: {len(failed_extractions)} SITs could not be extracted.")
            print("You may need to manually add these if needed.")
    else:
        print("ERROR: No GUIDs were successfully extracted.")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
