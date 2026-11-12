💡 **What:** Replaced the inefficient string concatenation (`text_content += ...`) within the PDF extraction loop with a fast `list.append()` and `str.join()` pattern. We explicitly check for `None` from `page.extract_text()` to avoid `TypeError` edge cases.

🎯 **Why:** In Python, string variables are immutable. Repeatedly concatenating strings inside a loop forces memory reallocation and data copying at every iteration, leading to quadratic time complexity O(N^2) for large texts. Using a list and `.join()` allows allocating the string just once, bringing the complexity down to O(N).

📊 **Measured Improvement:**
I created a benchmarking script that tested `extract_pdf_content.py` extraction speeds against short PDFs (1 page) and long PDFs (100+ pages), performing 10 trials per document to calculate average execution time.
- **`consort-spi.pdf` (1 page):** Baseline `0.5529s` | Improved `0.5270s` | Change `-0.0259s` (4.69% faster)
- **`prisma-scr.pdf` (2 pages):** Baseline `2.6818s` | Improved `2.6966s` | Change `+0.0148s` (0.55% slower)
- **`PRISMA_2020_examples.pdf` (134 pages):** Baseline `152.88s` | Improved `152.40s` | Change `-0.48s` (0.31% faster)

**Conclusion:**
While the `list.join` pattern is technically optimal and safer, the actual string reallocation overhead in Python proved to be extremely negligible compared to the underlying parsing operation performed by the `pdfplumber` module. The CPU bottleneck sits entirely within the `extract_text()` parsing process rather than the outer looping mechanism.

Despite not yielding an incredibly dramatic time save on large documents (a ~0.31% improvement), the new implementation is objectively safer by cleanly handling `None` edge cases that would crash the previous implementation, making it a valuable robustness update.
