"""One command for the whole month.

    python3 run.py

1. rebuilds data/flats.db from the CSVs and the bank export
2. runs the rent check (CSV per month + Bericht-YYYY-MM.md)
3. classifies new emails in data/inbox.csv into tickets
4. turns the newest Bericht into a PDF next to it (needs Google Chrome)
"""
import glob
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
PY = sys.executable
t0 = time.time()


def step(label, cmd):
    print(f"\n== {label}")
    r = subprocess.run([PY] + cmd, capture_output=True, text=True)
    print(r.stdout.strip()[-2000:])
    if r.returncode != 0:
        print(r.stderr.strip()[-2000:])
        print(f"!! {label} failed")
        sys.exit(1)


if not os.path.exists("data/umsaetze.txt"):
    print("Fehlt: data/umsaetze.txt (Sparkasse-Export als MT940 dort speichern)")
    sys.exit(1)

step("Datenbank", ["build_db.py"])
step("Mietcheck", ["rent_check.py"])
if os.path.exists("data/inbox.csv"):
    step("Posteingang", ["classify_emails.py", "inbox"])

# newest Bericht -> PDF
berichte = sorted(glob.glob("output/Bericht-*.md"))
if berichte:
    md_path = berichte[-1]
    html_path = md_path[:-3] + ".html"
    pdf_path = md_path[:-3] + ".pdf"
    try:
        import markdown
        body = markdown.markdown(open(md_path, encoding="utf-8").read())
    except ImportError:
        body = "<pre>" + open(md_path, encoding="utf-8").read() + "</pre>"
    html = ("<html><head><meta charset='utf-8'><style>body{font-family:Helvetica,Arial;"
            "font-size:12pt;margin:2cm;line-height:1.4}h1{font-size:20pt}h2{font-size:14pt;margin-top:1.2em}"
            "</style></head><body>" + body + "</body></html>")
    open(html_path, "w", encoding="utf-8").write(html)
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(chrome):
        subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={os.path.abspath(pdf_path)}", os.path.abspath(html_path)],
                       capture_output=True)
        print(f"\n== PDF: {pdf_path}")
    else:
        print(f"\n== Kein Chrome gefunden, Bericht als HTML: {html_path}")

print(f"\nFertig in {time.time() - t0:.1f} s.")
