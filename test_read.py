import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'prototype'))
from firefox_reader import get_firefox_bookmarks

db_path = os.environ.get('FIREFOX_PROFILE_PATH', './empty_chrome_profile/places.sqlite')

try:
    print(f"Reading {db_path}...")
    bms = get_firefox_bookmarks(db_path)
    print(f"Success! Read {len(bms)} bookmarks.")
except Exception as e:
    print(f"FAILED: {e}")
