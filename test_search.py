
import pytest
from flask import Flask
import sys
import os
os.environ['FLASK_ENV'] = 'testing'
# Add prototype to path so internal imports in api.py work
sys.path.append(os.path.abspath('prototype'))

from api import app, db, Bookmark
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        # Seed data
        b1 = Bookmark(title="Python Documentation", url="https://docs.python.org", source_browser="test", status="synced")
        b2 = Bookmark(title="Google Search", url="https://google.com", source_browser="test", status="synced")
        b3 = Bookmark(title="Flask Tutorial", url="https://flask.palletsprojects.com", source_browser="test", status="synced")
        db.session.add_all([b1, b2, b3])
        db.session.commit()
        
    with app.test_client() as client:
        yield client

def test_search_bookmarks(client):
    # Test 1: Search for "Python" (Should find b1)
    response = client.get('/bookmarks?q=Python')
    data = json.loads(response.data)
    print(f"DEBUG: Found {len(data['data'])} items for 'Python': {data['data']}")
    assert len(data['data']) == 1
    assert data['data'][0]['title'] == "Python Documentation"

    # Test 2: Search for "search" (Should find b2 by Title)
    response = client.get('/bookmarks?q=search')
    data = json.loads(response.data)
    assert len(data['data']) == 1
    assert data['data'][0]['title'] == "Google Search"

    # Test 3: Search for "flask" (Should find b3 by URL or Title)
    response = client.get('/bookmarks?q=flask')
    data = json.loads(response.data)
    assert len(data['data']) == 1
    assert data['data'][0]['title'] == "Flask Tutorial"

    # Test 4: Search for "nonexistent" (Should find nothing)
    response = client.get('/bookmarks?q=nonexistent')
    data = json.loads(response.data)
    assert len(data['data']) == 0

    # Test 5: No Query (Should find all)
    response = client.get('/bookmarks')
    data = json.loads(response.data)
    assert len(data['data']) == 3
