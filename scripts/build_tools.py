import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "tools.json"
OUTPUT_PATH = ROOT / "tools" / "tools.html"

def load_tools_data():
    if not DATA_PATH.exists():
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def render_tool_cards(tools):
    cards_html = []
    for tool in tools:
        card_html = f"""
            <article class="tool-card" id="{tool['id']}">
                <div class="tool-header">
                    <span class="status-badge">{tool['status']}</span>
                    <h2>{tool['title']}</h2>
                </div>
                <div class="tool-body">
                    <p>{tool['description']}</p>
                </div>
                <div class="tool-footer">
                    <span class="tool-note">{tool['note']}</span>
                </div>
            </article>
        """
        cards_html.append(card_html)
    return "\n".join(cards_html)

def main():
    data = load_tools_data()
    if not data:
        print(f"Error: {DATA_PATH} not found or empty.")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cards_html = render_tool_cards(data.get("tools", []))
    concept = data.get("concept", {})
    footer = data.get("footer_message", {})

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.get("page_title", "ツール一覧")}</title>
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="./tools.css">
</head>
<body>
    <header class="topbar">
        <div class="topbar-inner">
            <div class="brand-group">
                <div class="brand">つながろ ツール</div>
                <span class="coming-soon">Sample</span>
            </div>
            <nav class="menu-panel">
                <a href="../index.html">TOP</a>
                <a href="./tools.html">ツール一覧</a>
            </nav>
        </div>
    </header>

    <main class="container tools-container">
        <section class="portal-intro-box">
            <h2>{data.get("page_title", "")}</h2>
            <p>{concept.get("lead_text", "")}</p>
        </section>

        <section class="tool-list">
            {cards_html}
        </section>

        <section class="portal-footer-box">
            <h3>{footer.get("title", "")}</h3>
            <p>{footer.get("description", "")}</p>
        </section>
    </main>
</body>
</html>
"""

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
