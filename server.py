"""Simple web server with save endpoint for the family wiki."""

import os
import re
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, abort

WIKI_DIR = Path(
    os.environ.get("WIKI_DIR") or Path(__file__).resolve().parent / "wiki"
)
app = Flask(__name__, static_folder=None)


def extract_main_content(filepath):
    """Extract content between <main ...> and </main> from an HTML file."""
    html = filepath.read_text(encoding="utf-8")
    # Find the <main> tag and its content
    main_start = html.find("<main")
    if main_start == -1:
        return None, None
    main_open_end = html.find(">", main_start) + 1
    main_close = html.rfind("</main>")
    if main_close == -1:
        return None, None
    content = html[main_open_end:main_close]
    # Extract title
    title_match = re.search(r"<title>(.*?)</title>", html)
    title = title_match.group(1) if title_match else filepath.stem
    # Clean up HTML entities in title
    title = title.replace("&amp;", "&").replace("-", "-")
    # Remove " - Family Reference" suffix from titles
    title = re.sub(r"\s*-\s*(Family|Family).*$", "", title)
    return title, content


@app.route("/print-all")
def print_all():
    """Render all pages into a single printable document."""
    # Determine which section to print based on query param
    section = request.args.get("section", "person1")

    if section == "person2":
        page_order = [
            "person2/index.html",
            "person2/immediate/first-steps.html",
            "person2/immediate/employer.html",
            "person2/immediate/legal.html",
            "person2/immediate/pets.html",
            "person2/finance/banking.html",
            "person2/finance/insurance.html",
            "person2/finance/debts.html",
            "person2/finance/taxes.html",
            "person2/finance/crypto.html",
            "person2/finance/assets.html",
            "person2/digital/email.html",
            "person2/digital/social-media.html",
            "person2/digital/subscriptions.html",
            "person2/digital/domains.html",
            "person2/digital/photos.html",
            "person2/household/utilities.html",
            "person2/household/maintenance.html",
            "person2/household/keys-codes.html",
            "person2/personal/wishes.html",
            "person2/personal/letter.html",
        ]
        doc_title = "Person 2 - Family Reference"
    else:
        page_order = [
            "person1.html",
            "immediate/first-steps.html",
            "immediate/employer.html",
            "immediate/legal.html",
            "immediate/pets.html",
            "finance/banking.html",
            "finance/insurance.html",
            "finance/debts.html",
            "finance/taxes.html",
            "finance/crypto.html",
            "finance/assets.html",
            "digital/email.html",
            "digital/social-media.html",
            "digital/subscriptions.html",
            "digital/domains.html",
            "digital/photos.html",
            "household/utilities.html",
            "household/maintenance.html",
            "household/keys-codes.html",
            "personal/wishes.html",
            "personal/letter.html",
        ]
        doc_title = "Person 1 - Family Reference"

    # Build combined HTML
    sections_html = []
    for page_path in page_order:
        filepath = WIKI_DIR / page_path
        if not filepath.exists():
            continue
        title, content = extract_main_content(filepath)
        if content is None:
            continue
        sections_html.append(
            f'<section class="print-page">\n{content}\n</section>'
        )

    css_path = WIKI_DIR / "css" / "style.css"
    css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

    combined = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc_title} - Print All</title>
  <style>
    {css_content}

    /* Print-all overrides */
    body {{
      background: #fff;
      color: #000;
      font-family: 'Segoe UI', system-ui, sans-serif;
      line-height: 1.6;
      padding: 0;
      margin: 0;
    }}
    .print-page {{
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem 1.5rem;
      page-break-after: always;
    }}
    .print-page:last-child {{
      page-break-after: avoid;
    }}
    h1 {{ color: #333; font-size: 1.6rem; }}
    h2 {{ color: #333; font-size: 1.3rem; border-bottom: 2px solid #333; padding-bottom: 0.3rem; margin-top: 1.5rem; }}
    h3 {{ color: #006644; font-size: 1.05rem; }}
    table {{ border-collapse: collapse; width: 100%; margin: 0.75rem 0; font-size: 0.9rem; }}
    th {{ background: #f0f0f0; text-align: left; padding: 0.5rem; border: 1px solid #ccc; color: #006644; font-weight: 600; }}
    td {{ padding: 0.5rem; border: 1px solid #ccc; }}
    tr:nth-child(even) {{ background: #f9f9f9; }}
    code {{ background: #f0f0f0; padding: 0.1rem 0.3rem; border-radius: 3px; font-family: Consolas, monospace; font-size: 0.85rem; }}
    .info-box {{ background: #f0f7f4; border-left: 4px solid #006644; padding: 0.75rem 1rem; margin: 0.75rem 0; border-radius: 0 4px 4px 0; }}
    .warn-box {{ background: #fef9e7; border-left: 4px solid #886600; padding: 0.75rem 1rem; margin: 0.75rem 0; border-radius: 0 4px 4px 0; }}
    .crit-box {{ background: #fde8e8; border-left: 4px solid #cc0000; padding: 0.75rem 1rem; margin: 0.75rem 0; border-radius: 0 4px 4px 0; }}
    .badge {{ display: inline-block; padding: 0.1rem 0.4rem; border-radius: 3px; font-size: 0.75rem; font-weight: 600; }}
    .badge-ok {{ background: #e6f5ee; color: #006644; }}
    .badge-warn {{ background: #fff8e6; color: #886600; }}
    .badge-crit {{ background: #ffe6e6; color: #cc0000; }}
    .flow-diagram {{ background: #f5f5f5; border: 1px solid #ccc; border-radius: 6px; padding: 1rem; margin: 0.75rem 0; text-align: center; font-family: Consolas, monospace; font-size: 0.8rem; line-height: 1.8; white-space: pre; overflow-x: auto; }}
    .card-grid, .card, .page-footer, .page-subtitle {{ display: none; }}
    a {{ color: #006644; }}

    .print-header {{
      text-align: center;
      padding: 3rem 1.5rem;
      page-break-after: always;
    }}
    .print-header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
    .print-header p {{ color: #666; }}
    .print-toolbar {{
      position: fixed;
      top: 1rem;
      right: 1rem;
      z-index: 9999;
      display: flex;
      gap: 0.5rem;
    }}
    .print-toolbar button {{
      padding: 0.6rem 1.2rem;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 600;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }}
    .print-toolbar .print-btn {{ background: #006644; color: #fff; }}
    .print-toolbar .back-btn {{ background: #eee; color: #333; }}

    @media print {{
      .print-toolbar {{ display: none; }}
    }}
  </style>
</head>
<body>

  <div class="print-toolbar">
    <button class="print-btn" onclick="window.print()">Print / Save as PDF</button>
    <button class="back-btn" onclick="history.back()">Back</button>
  </div>

  <div class="print-header">
    <h1>{doc_title}</h1>
    <p>Complete reference document - all pages combined</p>
    <p style="font-size:0.85rem; color:#999;">Generated from wiki on {__import__('datetime').date.today().strftime('%B %d, %Y')}</p>
  </div>

  {"".join(sections_html)}

</body>
</html>"""

    return combined, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/save", methods=["POST"])
def save():
    """Save edited page content back to the HTML file."""
    data = request.get_json()
    if not data or "path" not in data or "content" not in data:
        return jsonify({"error": "Missing path or content"}), 400

    # Sanitize path to prevent directory traversal
    rel_path = data["path"].lstrip("/")
    if ".." in rel_path or rel_path.startswith("/"):
        return jsonify({"error": "Invalid path"}), 403

    file_path = WIKI_DIR / rel_path
    if not file_path.exists() or not file_path.suffix == ".html":
        return jsonify({"error": "File not found"}), 404

    # Read the existing file
    original = file_path.read_text(encoding="utf-8")

    # Replace the <main> content
    main_start = original.find("<main")
    main_open_end = original.find(">", main_start) + 1
    main_close = original.rfind("</main>")

    if main_start == -1 or main_close == -1:
        return jsonify({"error": "Could not find <main> element"}), 500

    new_html = original[:main_open_end] + "\n" + data["content"] + "\n  " + original[main_close:]
    file_path.write_text(new_html, encoding="utf-8")

    return jsonify({"ok": True})


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_file(path):
    """Serve static files from the wiki directory."""
    file_path = WIKI_DIR / path

    # If it's a directory, serve index.html inside it
    if file_path.is_dir():
        file_path = file_path / "index.html"
        path = str(Path(path) / "index.html")

    if not file_path.exists():
        abort(404)

    # For HTML files, inject the editor script before </body>
    if file_path.suffix == ".html":
        content = file_path.read_text(encoding="utf-8")
        editor_tag = '<script src="/edit.js"></script>'
        if editor_tag not in content:
            content = content.replace("</body>", f'  {editor_tag}\n</body>')
        return content, 200, {"Content-Type": "text/html; charset=utf-8"}

    # Guess MIME type for non-HTML files
    import mimetypes
    mime, _ = mimetypes.guess_type(str(file_path))
    return send_from_directory(str(file_path.parent), file_path.name, mimetype=mime)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("WIKI_HOST", "0.0.0.0"),
        port=int(os.environ.get("WIKI_PORT", "8080")),
    )
