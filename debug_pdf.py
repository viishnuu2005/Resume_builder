#!/usr/bin/env python
"""Debug PDF generation directly"""
import sys
sys.path.insert(0, '.')

from modules.pdf_generator import generate_pdf_resume

# Test with minimal data like the test does
data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '9876543210',
    'linkedin': 'linkedin.com/in/johndoe',
    'github': 'github.com/johndoe',
    'languages': 'English, Hindi',
    'template': 'modern',
    'education': '',
    'skills': 'Python',
    'projects': '',
    'experience': '',
    'certifications': '',
}

try:
    print("Attempting to generate PDF...")
    buffer, filename = generate_pdf_resume(data, 'modern')
    print(f"✓ PDF generated: {filename}")
    print(f"  Size: {len(buffer.getvalue())} bytes")
    if b'%PDF' in buffer.getvalue():
        print("  ✓ Valid PDF detected")
    else:
        print("  ✗ Not a valid PDF")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
