#!/usr/bin/env python3
"""
Simple test script for mini app routes
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_paths():
    """Test path resolution for mini app"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dist = os.path.abspath(os.path.join(current_dir, "frontend", "dist"))
    mini_app_path = os.path.join(frontend_dist, "mini-app.html")

    print(f"Current directory: {current_dir}")
    print(f"Frontend dist: {frontend_dist}")
    print(f"Mini app path: {mini_app_path}")
    print(f"Frontend dist exists: {os.path.exists(frontend_dist)}")
    print(f"Mini app exists: {os.path.exists(mini_app_path)}")

    if os.path.exists(frontend_dist):
        print(f"Frontend dist contents: {os.listdir(frontend_dist)}")

    if os.path.exists(os.path.join(frontend_dist, "assets")):
        print(f"Assets contents: {os.listdir(os.path.join(frontend_dist, 'assets'))}")

if __name__ == "__main__":
    test_paths()
