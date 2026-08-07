import os
import sys
import pytest

# Add scripts directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.find_latest_checklist import analyze_results

def test_empty_results():
    assert analyze_results([], "consort") == []

def test_zero_score_omitted():
    results = [
        {"title": "Some random article", "link": "http://example.com", "snippet": "Nothing useful here."}
    ]
    assert analyze_results(results, "consort") == []

def test_official_domain_score():
    results = [
        {"title": "Article", "link": "http://bmj.com/article", "snippet": "Snippet"}
    ]
    analyzed = analyze_results(results, "consort")
    assert len(analyzed) == 1
    assert analyzed[0]['score'] == 30

def test_title_keywords_score():
    results = [
        {"title": "Official Statement", "link": "http://example.com", "snippet": ""},
        {"title": "Latest Update", "link": "http://example.com", "snippet": ""}
    ]
    analyzed = analyze_results(results, "consort")
    assert len(analyzed) == 2
    # First candidate ("official statement" -> 20, actually both "official" and "statement" match the same condition which gives 20 once)
    # Wait, the code is:
    # if 'official' in title or 'statement' in title: score += 20
    # if 'update' in title or 'revision' in title or 'latest' in title: score += 15
    # So "Official Statement" gets 20.
    # "Latest Update" gets 15.

    # Sort order: 20 then 15
    assert analyzed[0]['score'] == 20
    assert analyzed[0]['title'] == "Official Statement"
    assert analyzed[1]['score'] == 15
    assert analyzed[1]['title'] == "Latest Update"

def test_snippet_keywords_score():
    results = [
        {"title": "Article", "link": "http://example.com", "snippet": "Here is the latest version of the guideline."}
    ]
    analyzed = analyze_results(results, "consort")
    assert len(analyzed) == 1
    assert analyzed[0]['score'] == 10

def test_year_detection_score():
    results = [
        {"title": "Article 2023", "link": "http://example.com", "snippet": "Also mentions 2010."},
    ]
    analyzed = analyze_results(results, "consort")
    assert len(analyzed) == 1
    # latest_year = max(2023, 2010) = 2023. Score = 2023 - 2000 = 23
    assert analyzed[0]['score'] == 23

def test_combined_score_and_sorting():
    results = [
        {"title": "A normal article", "link": "http://example.com", "snippet": ""}, # score 0, omitted
        {"title": "Official Statement 2024", "link": "http://bmj.com/article", "snippet": "latest version"},
        # score = 30 (bmj) + 20 (official/statement) + 10 (latest version) + 24 (2024) = 84
        {"title": "Update 2020", "link": "http://example.com", "snippet": ""},
        # score = 15 (update) + 20 (2020) = 35
    ]
    analyzed = analyze_results(results, "consort")
    assert len(analyzed) == 2
    assert analyzed[0]['title'] == "Official Statement 2024"
    assert analyzed[0]['score'] == 84

    assert analyzed[1]['title'] == "Update 2020"
    assert analyzed[1]['score'] == 35

def test_missing_keys_gracefully_handled():
    results = [
        {"title": "Official", "link": "http://example.com"}, # Missing snippet
        {"snippet": "latest version", "link": "http://example.com"}, # Missing title
        {"title": "update", "snippet": "snippet"} # Missing link
    ]
    analyzed = analyze_results(results, "consort")
    assert len(analyzed) == 3
    # Check that it didn't crash and processed them
    # "Official" -> 20
    # "latest version" -> 10
    # "update" -> 15

    assert analyzed[0]['score'] == 20
    assert analyzed[1]['score'] == 15
    assert analyzed[2]['score'] == 10
