import sys
sys.path.insert(0, 'c:/Users/viish/Downloads/Resume-Builder-ATS')
from modules import ats_analyzer

sample = """John Doe
johndoe@gmail.com +1234567890

Education
B.Tech Computer Science 2020

Experience
Software Engineer at TechCorp 2021-2023
Developed and optimized REST APIs using Python and Flask. Reduced response time by 30%.

Skills
Python, Flask, SQL, MongoDB, Git, Docker, AWS, React

Projects
Portfolio website using React and Node.js
Deployed on AWS with CI/CD pipeline
"""

res = ats_analyzer.analyze(sample)
print(f"Score: {res['score']}")
print(f"Grade: {res['grade']}")
print(f"Sections found: {res['sections_found']}")
print(f"Sections missing: {res['sections_missing']}")
print(f"Suggestions: {len(res['suggestions'])} tips")
for s in res['suggestions']:
    print(f"  - [{s['color']}] {s['title']}")
print(f"Word count: {res['word_count']}")
print(f"Keywords hit: {res['keyword_hits']}")
print(f"Has email: {res['has_email']}, Has phone: {res['has_phone']}")
