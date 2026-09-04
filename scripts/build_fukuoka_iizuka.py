import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "fukuoka-iizuka.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "fukuoka", "iizuka")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "iizuka.html")


def build_card_html(cards):
    html = ""
    for card in cards:
        html += f"""
            <article class="card">
                <img src="{card['image_url']}" alt="{card['title']}" class="card-image">
                <div class="card-body">
                    <span class="category-tag">{card['category']}</span>
                    <h3>{card['title']}</h3>
                    <p>{card['description']}</p>
                    <div class="card-footer">
                        <span>📍 {card['location']}</span>
                        <span>🕒 {card['date']}</span>
                    </div>
                </div>
            </article>
        """
    return html


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{data['page_title']} | つながろ</title>
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
            background: linear-gradient(180deg, #fffaf7 0%, var(--bg) 20%, var(--bg) 100%);
            color: var(--text);
        }}
        img {{ max-width: 100%; display: block; }}
        a {{ text-decoration: none; color: inherit; }}
        .topbar {{
            background: linear-gradient(135deg, var(--brand) 0%, #ff9a75 55%, #f2bb93 100%);
            color: white;
            box-shadow: 0 10px 30px rgba(255, 130, 80, 0.18);
        }}
        .topbar-inner {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 18px 20px;
        }}
        .brand {{
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.08em;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 28px 20px 60px;
        }}
        .hero {{
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 20px;
            margin-bottom: 24px;
        }}
        .hero-image {{
            border-radius: 26px;
            overflow: hidden;
            box-shadow: var(--shadow);
            border: 1px solid var(--line);
            min-height: 300px;
        }}
        .hero-image img {{
            width: 100%;
            height: 100%;
            min-height: 300px;
            object-fit: cover;
        }}
        .hero-copy {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 26px;
            padding: 26px 22px;
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .hero-copy h1 {{
            margin: 0 0 12px;
            font-size: clamp(2.2rem, 5vw, 3.2rem);
            letter-spacing: -0.06em;
            line-height: 1.05;
        }}
        .hero-copy p {{
            margin: 0;
            color: var(--sub);
            line-height: 1.8;
            font-size: 0.96rem;
        }}
        .card-list {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 22px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }}
        .card-image {{
            width: 100%;
            height: 220px;
            object-fit: cover;
            display: block;
        }}
        .card-body {{
            padding: 18px 18px 16px;
        }}
        .category-tag {{
            display: inline-block;
            padding: 7px 10px;
            border-radius: 999px;
            background: #fff2ea;
            color: var(--brand-dark);
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
        .card h3 {{
            margin: 12px 0 8px;
            font-size: 1.25rem;
            letter-spacing: -0.03em;
        }}
        .card p {{
            margin: 0 0 12px;
            color: var(--sub);
            line-height: 1.8;
            font-size: 0.92rem;
        }}
        .card-footer {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
            border-top: 1px solid var(--line);
            padding-top: 12px;
            color: var(--sub);
            font-size: 0.76rem;
            font-weight: 700;
        }}
        @media (max-width: 820px) {{
            .hero, .card-list {{ grid-template-columns: 1fr; }}
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
            <div class="hero-image">
                <img src="{data['hero_image']}" alt="{data['page_title']}" />
            </div>
            <div class="hero-copy">
                <h1>{data['page_title']}</h1>
                <p>{data['hero_description']}</p>
            </div>
        </section>

        <section class="card-list">
            {build_card_html(data['cards'])}
        </section>
    </main>
</body>
</html>
"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("✨ 飯塚ページを更新しました")


if __name__ == "__main__":
    main()
