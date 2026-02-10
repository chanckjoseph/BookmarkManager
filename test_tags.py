
import pytest
import sys
import os
import json

os.environ['FLASK_ENV'] = 'testing'
sys.path.append(os.path.abspath('prototype'))

from api import app, db, Bookmark, Tag

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        # Seed a bookmark
        b1 = Bookmark(title="Test Page", url="http://example.com", source_browser="test")
        db.session.add(b1)
        db.session.commit()
        
    with app.test_client() as client:
        yield client

def test_tag_lifecycle(client):
    # 1. Create a Tag explicitly
    res = client.post('/tags', json={"name": "Work"})
    assert res.status_code == 200
    data = json.loads(res.data)
    tag_id = data['data']['id']
    assert data['data']['name'] == "Work"

    # 2. Attach Tag to Bookmark
    # First get the bookmark ID (should be 1)
    res = client.post(f'/bookmarks/1/tags', json={"name": "Work"})
    assert res.status_code == 200
    data = json.loads(res.data)
    tag_names = [t['name'] for t in data['data']['tags']]
    assert "Work" in tag_names

    # 3. Attach a NEW tag (implicit creation)
    res = client.post(f'/bookmarks/1/tags', json={"name": "Research"})
    assert res.status_code == 200
    data = json.loads(res.data)
    tag_names = [t['name'] for t in data['data']['tags']]
    assert "Research" in tag_names
    assert "Work" in tag_names

    # 4. List Tags
    res = client.get('/tags')
    data = json.loads(res.data)
    assert len(data['data']) == 2
    
    # 5. Remove Tag
    # Need to find the ID of "Work" tag.
    tag_work = next(t for t in data['data'] if t['name'] == 'Work')
    
    res = client.delete(f'/bookmarks/1/tags/{tag_work["id"]}') # Removing "Work"
    assert res.status_code == 200
    data = json.loads(res.data)
    tag_names = [t['name'] for t in data['data']['tags']]
    assert "Work" not in tag_names
    assert "Research" in tag_names
