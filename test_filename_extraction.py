"""Test filename extraction from Content-Disposition header."""
import re

# Test cases for filename extraction
test_cases = [
    ('attachment; filename="Srikaran_cv.docx"', 'Srikaran_cv.docx', 'Quoted filename'),
    ('attachment; filename=Srikaran_cv.docx', 'Srikaran_cv.docx', 'Unquoted filename'),
    ('attachment; filename="John Smith_cv.docx"', 'John Smith_cv.docx', 'Quoted with spaces'),
    ('attachment; filename*=UTF-8\'\'John%20Smith_cv.docx', 'John Smith_cv.docx', 'RFC 5987 encoded'),
]

print('Testing filename extraction from Content-Disposition header\n')

for header, expected, desc in test_cases:
    filename = 'resume.docx'
    
    # Try RFC 5987 encoded first
    matches = re.search(r"filename\*=(?:UTF-8'')?([^;]+)", header, re.IGNORECASE)
    if matches and matches.group(1):
        # Decode URL-encoded filename
        import urllib.parse
        filename = urllib.parse.unquote(matches.group(1).strip())
    else:
        # Try standard filename= (quoted or unquoted)
        matches = re.search(r'filename=(?:"([^"]*)"|([^;,\s]*))', header, re.IGNORECASE)
        if matches and (matches.group(1) or matches.group(2)):
            filename = (matches.group(1) or matches.group(2)).strip()
    
    status = '✓ PASS' if filename == expected else '✗ FAIL'
    print(f'{status} | {desc}')
    print(f'  Header: {header}')
    print(f'  Expected: {expected}')
    print(f'  Got: {filename}\n')
