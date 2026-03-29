#!/usr/bin/env python
"""Test all critical endpoints and functionality"""
import requests
import json
from io import BytesIO

BASE_URL = "http://127.0.0.1:5000"

def test_homepage():
    """Test that homepage loads"""
    print("Testing homepage...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, f"Homepage failed: {response.status_code}"
    assert "Resume" in response.text or "resume" in response.text.lower()
    print("✓ Homepage loads successfully")

def test_dashboard():
    """Test dashboard endpoint"""
    print("\nTesting dashboard...")
    response = requests.get(f"{BASE_URL}/dashboard")
    assert response.status_code == 200, f"Dashboard failed: {response.status_code}"
    print("✓ Dashboard loads successfully")

def test_analyze_role_page():
    """Test analyze role page loads"""
    print("\nTesting analyze role page...")
    response = requests.get(f"{BASE_URL}/analyze-role")
    assert response.status_code == 200, f"Analyze role page failed: {response.status_code}"
    assert "role" in response.text.lower()
    print("✓ Analyze role page loads successfully")

def test_pdf_generation_minimal():
    """Test PDF generation with minimal form data"""
    print("\nTesting PDF generation...")
    
    # Create minimal form data - matching actual HTML form structure
    # Note: Form fields with [] are array fields that should be empty strings/lists
    # When form is posted, empty fields are just not included
    form_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '9876543210',
        'linkedin': 'linkedin.com/in/johndoe',
        'github': 'github.com/johndoe',
        'languages': 'English, Hindi',
        'template_id': 'modern',  # Changed from 'template' to 'template_id'
        'skills': 'Python',
        'hasExperience': 'false',  # string 'false' not boolean
    }
    
    response = requests.post(f"{BASE_URL}/preview", data=form_data)
    
    if response.status_code == 200:
        # Check if we got a PDF
        if b'%PDF' in response.content:
            print("✓ PDF generation works - valid PDF returned")
            return True
        else:
            print(f"✗ PDF generation returned {len(response.content)} bytes but not a PDF file")
            print(f"  Content-Type: {response.headers.get('Content-Type')}")
            return False
    else:
        print(f"✗ PDF generation failed with status {response.status_code}")
        print(f"  Full Response:\n{response.text}")
        return False

def test_district_loading():
    """Test district dropdown by checking if districts data is in the HTML"""
    print("\nTesting district dropdown data...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    
    # Check if indiaStateDistricts variable is in the page
    if "indiaStateDistricts" in response.text and "Kerala" in response.text:
        # Check for some districts
        if "Thiruvananthapuram" in response.text or "Kochikode" in response.text:
            print("✓ District data loaded in page")
            return True
        else:
            print("✗ District data exists but appears incomplete")
            return False
    else:
        print("✗ District data not found in page")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("TESTING RESUME BUILDER ATS")
    print("=" * 60)
    
    try:
        test_homepage()
        test_dashboard()
        test_analyze_role_page()
        test_district_loading()
        pdf_works = test_pdf_generation_minimal()
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        if pdf_works:
            print("✓ All critical endpoints working!")
        else:
            print("⚠ Some endpoints have issues - check details above")
        
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {BASE_URL}")
        print("  Make sure Flask server is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"✗ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
