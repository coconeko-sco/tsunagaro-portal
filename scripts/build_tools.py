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
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-6LHJQFWKTQ"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-6LHJQFWKTQ');
    </script>
    <title>{data.get("page_title", "ツール一覧")}</title>
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="./tools.css">
</head>
<body>
    <header class="topbar">
        <div class="topbar-inner">
            <div class="brand-group">
                <div class="brand">つながろ ツール</div>
                <span class="coming-soon">Coming soon...</span>
            </div>
            <div class="menu-container" style="position: relative;">
                <button class="menu-toggle" id="menuToggle" aria-label="メニューを開閉" style="background: none; border: none; cursor: pointer; padding: 8px; color: #334155;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                </button>
                <nav class="menu-panel" id="menuPanel" style="display: none; position: absolute; right: 0; top: 100%; background: #fff; border: 1px solid #cbd5e1; border-radius: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 8px 0; min-width: 140px; z-index: 100;">
                    <a href="../index.html" style="display: block; padding: 8px 16px; color: #334155; text-decoration: none;">TOP</a>
                    <a href="./tools.html" style="display: block; padding: 8px 16px; color: #334155; text-decoration: none;">ツール一覧</a>
                </nav>
            </div>
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

    <script>
        const toggleBtn = document.getElementById('menuToggle');
        const menuPanel = document.getElementById('menuPanel');
        if (toggleBtn && menuPanel) {
            toggleBtn.addEventListener('click', (e) => {{
                e.stopPropagation();
                menuPanel.style.display = menuPanel.style.display === 'block' ? 'none' : 'block';
            }});
            document.addEventListener('click', () => {{
                menuPanel.style.display = 'none';
            }});
        }
    </script>
</body>
</html>
"""

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
