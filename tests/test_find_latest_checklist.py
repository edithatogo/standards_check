import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.find_latest_checklist import mock_google_search, analyze_results, main

def test_mock_google_search_returns_empty_list():
    result = mock_google_search("test query")
    assert result == []

def test_mock_google_search_prints_query(capsys):
    query = "consort guidelines 2024"
    mock_google_search(query)
    captured = capsys.readouterr()
    assert f"--> Mock Search: '{query}'" in captured.out

def test_analyze_results_official_domain():
    results = [
        {'title': 'Some page', 'snippet': 'Some snippet', 'link': 'https://example.com/test'},
        {'title': 'Official CONSORT', 'snippet': 'Here it is', 'link': 'https://consort-statement.org/latest'}
    ]
    ranked = analyze_results(results, 'consort')
    assert len(ranked) == 1
    # 30 for domain + 20 for 'official' in title
    assert ranked[0]['score'] == 50

def test_analyze_results_keywords():
    results = [
        {'title': 'official statement latest', 'snippet': 'latest version updated guideline', 'link': 'https://example.com/test'}
    ]
    ranked = analyze_results(results, 'consort')
    assert len(ranked) == 1
    # 20 (title: official/statement) + 15 (title: latest/revision/update) + 10 (snippet: latest version/updated guideline) = 45
    assert ranked[0]['score'] == 45

def test_analyze_results_year_detection():
    results = [
        {'title': 'Guidelines 2022', 'snippet': 'Updated in 2023', 'link': 'https://example.com/test'}
    ]
    ranked = analyze_results(results, 'consort')
    assert len(ranked) == 1
    # 2023 - 2000 = 23
    assert ranked[0]['score'] == 23

def test_analyze_results_multiple():
    results = [
        {'title': 'Guidelines', 'snippet': 'Test', 'link': 'https://example.com'}, # score 0
        {'title': 'Official Guidelines 2020', 'snippet': 'Latest version', 'link': 'https://bmj.com/test'}
        # domain 30 + title 20 ('official') + snippet 10 ('latest version') + year 20 ('2020') = 80
    ]
    ranked = analyze_results(results, 'consort')
    assert len(ranked) == 1
    assert ranked[0]['score'] == 80
    assert ranked[0]['link'] == 'https://bmj.com/test'

def test_main_no_args(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['find_latest_checklist.py'])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "Usage:" in captured.out

def test_main_with_args(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['find_latest_checklist.py', 'consort'])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "Searching for the latest version of 'consort'" in captured.out
    assert "Could not retrieve search results." in captured.out

def test_main_with_results(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['find_latest_checklist.py', 'consort'])

    def mock_search(query):
        return [
            {'title': 'Official CONSORT Statement 2024', 'snippet': 'The updated guideline', 'link': 'https://consort-statement.org/2024'}
        ]

    monkeypatch.setattr('scripts.find_latest_checklist.mock_google_search', mock_search)

    main()
    captured = capsys.readouterr()
    assert "--- Top Candidates ---" in captured.out
    assert "Official CONSORT Statement 2024" in captured.out
    assert "Link: https://consort-statement.org/2024" in captured.out

def test_main_with_results_but_no_candidates(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['find_latest_checklist.py', 'consort'])

    def mock_search(query):
        return [
            {'title': 'Random stuff', 'snippet': 'Nothing here', 'link': 'https://example.com/'}
        ]

    monkeypatch.setattr('scripts.find_latest_checklist.mock_google_search', mock_search)

    main()
    captured = capsys.readouterr()
    assert "--- Top Candidates ---" in captured.out
    assert "No strong candidates found" in captured.out

def test_analyze_results_missing_fields():
    results = [
        {'title': 'Just title'} # no link, no snippet
    ]
    ranked = analyze_results(results, 'consort')
    assert len(ranked) == 0
