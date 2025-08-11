#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Find Latest Checklist Version
=============================

This script assists in finding the latest version of a given checklist
by searching the web and analyzing the results.

It does not automatically ingest or update files but provides a ranked
list of candidate URLs for the user to investigate.

Prerequisites:
--------------
1. Python 3.7+
2. Required libraries, which can be installed via pip:
   `pip install -r scripts/requirements.txt`
3. An environment variable `GEMINI_API_KEY` for the web search functionality.

Usage:
------
`python scripts/find_latest_checklist.py <checklist_group>`

Argument:
----------
- `checklist_group`: The name of the checklist to search for (e.g., "consort", "prisma").

Example:
--------
`python scripts/find_latest_checklist.py consort`

"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

# Mock search function for local development.
# In a real scenario, this would be replaced by an actual call to a search tool.
def mock_google_search(query):
    print(f"--> Mock Search: '{query}'")
    # In a real implementation, you would use a tool like the `google_web_search`
    # available in the environment this script is designed for.
    # For now, this function will return a hardcoded, empty list.
    # To make this script fully functional, you would need to integrate
    # with an actual search API or tool.
    return []

def analyze_results(results, group):
    """Analyzes and ranks search results."""
    ranked_candidates = []
    year_pattern = re.compile(r'\b(20\d{2})\b') # Finds years like 2023, 2010, etc.

    for result in results:
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        link = result.get('link', '')
        
        score = 0
        
        # --- Scoring Logic ---
        # Higher score for official-sounding domains
        if any(domain in urlparse(link).netloc for domain in ['bmj.com', 'jamanetwork.com', 'prisma-statement.org', 'consort-statement.org']):
            score += 30
        
        # Keywords in title
        if 'official' in title or 'statement' in title:
            score += 20
        if 'update' in title or 'revision' in title or 'latest' in title:
            score += 15
            
        # Keywords in snippet
        if 'latest version' in snippet or 'updated guideline' in snippet:
            score += 10
            
        # Year detection
        years = year_pattern.findall(title + snippet)
        if years:
            # Give more weight to more recent years
            latest_year = max([int(y) for y in years])
            score += (latest_year - 2000) # Add points based on how recent the year is
            
        if score > 0:
            ranked_candidates.append({
                "score": score,
                "title": result.get('title'),
                "link": link,
                "snippet": result.get('snippet')
            })

    # Sort by score in descending order
    return sorted(ranked_candidates, key=lambda x: x['score'], reverse=True)


def main():
    if len(sys.argv) != 2:
        print("Usage: python find_latest_checklist.py <checklist_group>")
        sys.exit(1)
        
    checklist_group = sys.argv[1]
    print(f"Searching for the latest version of '{checklist_group}'...\n")
    
    # Construct a query designed to find official sources
    query = f'{checklist_group} statement latest version official guidelines'
    
    # This is where the actual search would happen.
    # As noted in the function, this is a mock for demonstration.
    search_results = mock_google_search(query)
    
    if not search_results:
        print("Could not retrieve search results.")
        print("This script is a prototype and requires integration with a search tool.")
        print("Please manually search for your checklist.")
        sys.exit(0)

    candidates = analyze_results(search_results, checklist_group)
    
    print("--- Top Candidates ---")
    if not candidates:
        print("No strong candidates found. Please try a manual web search.")
    else:
        for i, candidate in enumerate(candidates[:5]): # Show top 5
            print(f"\n{i+1}. {candidate['title']}")
            print(f"   Link: {candidate['link']}")
            print(f"   Score: {candidate['score']}")
            print(f"   Snippet: {candidate['snippet']}")
            
    print("\n--- Next Steps ---")
    print("Review the links above to identify the correct new version.")
    print("Once you have the source URL, you can start the ingestion process by creating a new YAML file in the `source/` directory.")


if __name__ == "__main__":
    main()
