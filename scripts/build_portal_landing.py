import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "portal_landing.json")
OUTPUT_DIR = BASE_DIR
OUTPUT_FILE = os.path.join(BASE_DIR, "index.html")


def build_region_links(regions):
    cards = ""
    for region in regions:
        href = region.get("href", "#")
        name = region.get("name", "地域")
        description = region.get("description", "")
        cards += f"""
            <article class="region-card">
                <h3>{name}</h3>
                <p>{description}</p>
                <a href="{href}">{name}を見る</a>
            </article>
        """
    return cards


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    regions = data.get("regions", [])

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>つながろ - 地域を選ぶ</title>
    <style>
        :root {{
            --brand: #ff7a3d;
            --brand-dark: #d85d22;
            --bg: #f5f7fb;
            --panel: #ffffff;
            --line: #ebeff5;
            --text: #1f2937;
            --sub: #58657a;
            --shadow: 0 14px 34px rgba(17, 24, 39, 0.08);
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(180deg, #fffaf7 0%, var(--bg) 25%, var(--bg) 100%);
            color: var(--text);
        }}
        a {{ text-decoration: none; color: inherit; }}
        .topbar {{
            background: linear-gradient(135deg, var(--brand) 0%, #ff9a75 55%, #f2bb93 100%);
            color: white;
            box-shadow: 0 10px 30px rgba(255, 130, 80, 0.18);
        }}
        .topbar-inner {{
            max-width: 980px;
            margin: 0 auto;
            padding: 18px 20px;
        }}
        .brand {{
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.08em;
        }}
        .container {{
            max-width: 980px;
            margin: 0 auto;
            padding: 28px 20px 60px;
        }}
        .hero {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 26px;
            padding: 28px 24px;
            box-shadow: var(--shadow);
            margin-bottom: 22px;
        }}
        .hero h1 {{
            margin: 0 0 10px;
            font-size: clamp(2rem, 4vw, 3rem);
            letter-spacing: -0.06em;
        }}
        .hero p {{
            margin: 0;
            color: var(--sub);
            line-height: 1.8;
            font-size: 0.96rem;
        }}
        .region-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
        }}
        .region-card {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 20px 18px;
            box-shadow: var(--shadow);
        }}
        .region-card h3 {{
            margin: 0 0 8px;
            font-size: 1.5rem;
            letter-spacing: -0.04em;
        }}
        .region-card p {{
            margin: 0 0 16px;
            color: var(--sub);
            line-height: 1.8;
            font-size: 0.9rem;
        }}
        .region-card a {{
            display: inline-block;
            padding: 10px 14px;
            border-radius: 12px;
            background: var(--brand);
            color: white;
            font-weight: 700;
            font-size: 0.8rem;
        }}
        @media (max-width: 760px) {{
            .region-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header class="topbar">
        <div class="topbar-inner">
            <div class="brand">つながろ</div>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <h1>地域を選ぶ</h1>
            <p>地域ごとのおすすめを選んで、地元の話題を見ていきましょう。</p>
        </section>

        <section class="region-grid">
            {build_region_links(regions)}
        </section>
    </main>
</body>
</html>
"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("✨ ランディングページを更新しました")


if __name__ == "__main__":
    main()
