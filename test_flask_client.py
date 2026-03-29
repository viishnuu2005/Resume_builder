#!/usr/bin/env python
"""Test Flask routes directly using test client"""
import sys
from app import app

client = app.test_client()

# Test PDF generation with test client
print("Testing PDF generation with Flask test client...")

form_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '9876543210',
    'linkedin': 'linkedin.com/in/johndoe',
    'github': 'github.com/johndoe',
    'languages': 'English, Hindi',
    'template_id': 'modern',
    'skills': 'Python',
    'hasExperience': 'false',
}

response = client.post('/preview', data=form_data)

print(f"Status: {response.status_code}")
print(f"Response type: {type(response.data).__name__}")

if response.status_code == 200:
    if b'%PDF' in response.data:
        print("✓ PDF generation successful!")
        print(f"  PDF size: {len(response.data)} bytes")
    else:
        print("✗ Response not a PDF")
        print(f"  Content: {response.data[:200]}")
else:
    print(f"✗ Error: {response.status_code}")
    print(f"  Response: {response.data.decode('utf-8', errors='replace')[:1000]}")
