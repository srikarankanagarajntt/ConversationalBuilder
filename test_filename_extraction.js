// Test filename extraction from Content-Disposition header

const testCases = [
  {
    header: 'attachment; filename="Srikaran_cv.docx"',
    expected: 'Srikaran_cv.docx',
    desc: 'Quoted filename (RFC 5987)'
  },
  {
    header: 'attachment; filename=Srikaran_cv.docx',
    expected: 'Srikaran_cv.docx',
    desc: 'Unquoted filename'
  },
  {
    header: 'attachment; filename="John Smith_cv.docx"',
    expected: 'John Smith_cv.docx',
    desc: 'Quoted filename with spaces'
  },
  {
    header: 'attachment; filename*=UTF-8\'\'John%20Smith_cv.docx',
    expected: 'John Smith_cv.docx',
    desc: 'RFC 5987 encoded filename'
  }
];

testCases.forEach(test => {
  let filename = 'resume.docx'; // fallback
  const contentDisposition = test.header;
  
  if (contentDisposition) {
    // Try RFC 5987 encoded filename first (filename*=)
    let matches = contentDisposition.match(/filename\*=(?:UTF-8'')?([^;]+)/i);
    if (matches && matches[1]) {
      // Decode URL-encoded filename
      filename = decodeURIComponent(matches[1]).trim();
    } else {
      // Try standard filename= (quoted or unquoted)
      matches = contentDisposition.match(/filename=(?:"([^"]*)"|([^;,\s]*))/i);
      if (matches && (matches[1] || matches[2])) {
        filename = (matches[1] || matches[2]).trim();
      }
    }
  }
  
  const pass = filename === test.expected ? '✓ PASS' : '✗ FAIL';
  console.log(`${pass} | ${test.desc}`);
  console.log(`  Header: ${test.header}`);
  console.log(`  Expected: ${test.expected}`);
  console.log(`  Got: ${filename}`);
  console.log();
});
