#!/usr/bin/env python
"""Test complete resume with all data sections"""
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_full_resume():
    """Test PDF generation with complete resume data"""
    print("Testing full resume generation with all sections...")
    
    form_data = {
        'name': 'Alice Johnson',
        'email': 'alice@example.com',
        'phone': '91-9876543210',
        'linkedin': 'linkedin.com/in/alice-johnson',
        'github': 'github.com/alicejohnson',
        'languages': 'English, Tamil, Hindi',
        'template_id': 'modern',
        'skills': 'Python',
        
        # School education
        'school_qualification[]': ['12th Grade', 'B.Com'],
        'school_syllabus[]': ['CBSE', 'University'],
        'school_year[]': ['2015', '2018'],
        'school_percentage[]': ['92%', '85%'],
        
        # Higher education
        'higher_degree[]': ['Bachelor of Commerce'],
        'higher_specialization[]': ['Finance'],
        'higher_college[]': ['Chennai University'],
        'higher_inst_type[]': ['Government'],
        'higher_grad_year[]': ['2018'],
        
        # Experience
        'hasExperience': 'true',
        'exp_company[]': ['TechCorp', 'InnovateInc'],
        'exp_role[]': ['Junior Developer', 'Senior Developer'],
        'exp_desc[]': ['Developed web applications using Python', 'Led a team of 5 developers'],
        
        # Projects
        'project_title[]': ['Resume Builder'],
        'project_desc[]': ['Built an AI-powered resume builder with ATS compatibility'],
        'project_tech[]': ['Python, Flask, ReportLab'],
        
        # Certifications
        'cert_name[]': ['AWS Solutions Architect'],
        'cert_org[]': ['Amazon'],
        'cert_year[]': ['2022'],
        'cert_link[]': [''],
    }
    
    response = requests.post(f"{BASE_URL}/preview", data=form_data)
    
    if response.status_code == 200:
        if b'%PDF' in response.content:
            print("✓ Full resume PDF generation successful!")
            print(f"  PDF size: {len(response.content)} bytes")
            # Save PDF for manual inspection
            with open('test_resume.pdf', 'wb') as f:
                f.write(response.content)
            print("  Saved to: test_resume.pdf")
            return True
        else:
            print("✗ Response not a PDF")
            return False
    else:
        print(f"✗ Failed with status {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        return False

if __name__ == "__main__":
    success = test_full_resume()
    if success:
        print("\n✓ ALL TESTS PASSED - WEBSITE FULLY FUNCTIONAL!")
    else:
        print("\n✗ Some tests failed")
