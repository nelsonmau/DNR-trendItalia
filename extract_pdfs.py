import fitz
import re
from pathlib import Path

PDF_DIR = Path(__file__).parent
OUT_DIR = PDF_DIR / "extracted"
OUT_DIR.mkdir(exist_ok=True)

COUNTRY_PATTERN = re.compile(
    r"Digital News Report \d{4}\s*\|\s*(.+)", re.IGNORECASE
)


def extract_pdf(pdf_path: Path) -> None:
    year = re.search(r"\d{4}", pdf_path.name).group()
    doc = fitz.open(pdf_path)
    out_path = OUT_DIR / f"Digital_News_Report_{year}.md"

    lines = []
    lines.append(f"# Reuters Institute Digital News Report {year}\n")

    current_country = None

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if not text:
            continue

        # Detect country section header
        match = COUNTRY_PATTERN.search(text)
        if match:
            country = match.group(1).strip()
            if country != current_country:
                current_country = country
                lines.append(f"\n## {country}\n")

        # Clean up the text
        cleaned = text
        # Remove repeated page number lines like "81\n"
        cleaned = re.sub(r"^\d+\s*\n", "", cleaned, flags=re.MULTILINE)

        lines.append(cleaned)
        lines.append("\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[{year}] {page_num} pages → {out_path.name}")


if __name__ == "__main__":
    pdfs = sorted(PDF_DIR.glob("Digital_News_Report_*.pdf"))
    print(f"Found {len(pdfs)} PDFs\n")
    for pdf in pdfs:
        extract_pdf(pdf)
    print("\nDone. Files saved in ./extracted/")
