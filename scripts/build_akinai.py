import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "akinai.json"
OUTPUT_PATH = ROOT / "akinai" / "akinai.html"

def load_akinai():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def render_card(item):
    cat = item["category"]
    t_type = item["transaction_type"]
    
    t_type_labels = {
        "sell": "売ります",
        "give": "あげます",
        "rent": "貸します"
    }
    t_label = t_type_labels.get(t_type, t_type)

    invoice_badge = '<span class="badge-tag invoice">インボイス対応</span>' if item.get("invoice") else ''
    receipt_badge = '<span class="badge-tag receipt">領収書発行可</span>' if item.get("receipt") else ''
    
    photos = item.get("images", [])
    photos_html = "".join([f'<img src="{p}" alt="{item["seller_info"]["store_name"]}" loading="lazy">' for p in photos])

    seller = item["seller_info"]
    
    details_rows = ""
    if cat == "item":
        d = item.get("item_details", {})
        details_rows = f"""
            <tr><th>仕様・サイズ</th><td>{d.get("spec", "-")}</td></tr>
            <tr><th>商品の状態</th><td>{d.get("condition", "-")}</td></tr>
            <tr><th>引き渡し可能日</th><td>{d.get("available_date", "-")}</td></tr>
            <tr><th>引き取り方法</th><td>{d.get("delivery_method", "-")}</td></tr>
        """
    elif cat == "space":
        d = item.get("space_details", {})
        details_rows = f"""
            <tr><th>利用可能時間</th><td>{d.get("available_hours", "-")}</td></tr>
            <tr><th>利用開始日</th><td>{d.get("available_date", "-")}</td></tr>
            <tr><th>物件オーナー区分</th><td>{d.get("owner_type", "-")}</td></tr>
            <tr><th>保健所営業許可</th><td>{d.get("health_license_type", "-")}</td></tr>
            <tr><th>光熱費など</th><td>{d.get("utility_fee", "-")}</td></tr>
            <tr><th>利用想定目的</th><td>{d.get("usage_purpose", "-")}</td></tr>
        """

    # 登録されている連絡手段を「動作しない見た目だけのボタン」として生成する
    contacts = seller.get("contacts", {})
    contact_buttons = []
    
    if "line" in contacts and contacts["line"]:
        contact_buttons.append(f'<a href="#" onclick="return false;" class="contact-btn line-btn" style="cursor: default;">💬 LINEで店主へ直接問い合わせる</a>')
    
    if "phone" in contacts and contacts["phone"]:
        contact_buttons.append(f'<a href="#" onclick="return false;" class="contact-btn phone-btn" style="cursor: default;">📞 直通電話で問い合わせ ({contacts["phone"]})</a>')
        
    if "email" in contacts and contacts["email"]:
        contact_buttons.append(f'<a href="#" onclick="return false;" class="contact-btn mail-btn" style="cursor: default;">✉️ メールで問い合わせる</a>')

    contact_btn_html = "".join(contact_buttons)

    return f"""
    <article class="job-card akinai-card" data-category="{cat}" data-transaction="{t_type}" data-area="{seller["area"]}" id="{item["id"]}">
        <div class="job-header">
            <div class="job-meta-row">
                <span class="category-tag">{"商い物品" if cat=="item" else "スペース・間借り"}</span>
                <span class="employment-badge">{t_label}</span>
                <span class="area-badge">📍 {seller["area"]}</span>
                {invoice_badge}
                {receipt_badge}
            </div>
            <h2>{item["title"]}</h2>
            <div class="store-info-bar">
                <strong>{seller["store_name"]}</strong>
                <span><a href="{seller["store_url"]}" target="_blank">店舗情報・詳細ウェブサイト</a></span>
            </div>
        </div>

        <div class="job-body-grid">
            <div class="job-photos">
                {photos_html}
            </div>
            <div class="job-details-list">
                <div class="salary-box akinai-price-box">
                    <span class="salary-label">希望価格 / 賃料</span>
                    <span class="salary-amount">{item["price"]}</span>
                </div>
                
                <table class="job-table">
                    {details_rows}
                    <tr><th>連絡推奨時間</th><td class="highlight-time">✅ {seller.get("preferred_contact_time", "特になし")}</td></tr>
                </table>
            </div>
        </div>

        <div class="job-footer-action akinai-footer-action">
            {contact_btn_html}
            <p class="disclaimer-note">※当サイトは情報掲載のみを行います。取引・契約・搬出作業・保健所への届出等はすべて当事者間の自己責任となります。</p>
        </div>
    </article>
    """

def main():
    items = load_akinai()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cards_html = "".join([render_card(item) for item in items])

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-6LHJQFWKTQ"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-6LHJQFWKTQ');
    </script>
    <title>つながろ 商いマッチ | 地域店舗の不用品・厨房機器・間借りスペース掲示板</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header class="topbar">
        <div class="topbar-inner">
            <div class="brand-group">
                <div class="brand">つながろ 商いマッチ</div>
                <span class="coming-soon">Coming soon...</span>
            </div>
            <button class="menu-button" type="button" aria-label="メニューを開く" aria-expanded="false" aria-controls="site-menu">
                <span></span><span></span><span></span>
            </button>
            <nav class="menu-panel" id="site-menu" hidden>
                <a href="../index.html">TOP</a>
                <a href="./akinai.html">商いマッチ</a>
            </nav>
        </div>
    </header>

    <main class="container job-portal-container">
        <!-- 案内セクション -->
        <section class="portal-intro-box" style="background: #fdf8f6; border-left: 4px solid #d97706; padding: 16px; margin-bottom: 24px; border-radius: 4px;">
            <h2 style="font-size: 1.1rem; margin-bottom: 8px; color: #92400e;">🤝 商いマッチ（店舗間シェア・譲渡掲示板）</h2>
            <p style="font-size: 0.9rem; color: #4b5563; line-height: 1.6;">
                筑豊エリアの飲食店・商店で使える「厨房機器・不用品の売買/譲渡」や「空きスペース・間借りキッチンのシェア」等に特化した掲示板です。店主同士が直接つながるクリーンなローカルプラットフォームです。（※決済や仲介は行いません。当事者間の自己責任となります）
            </p>
        </section>

        <!-- 検索・フィルターバー -->
        <section class="filter-section">
            <div class="filter-group">
                <label>カテゴリ</label>
                <select id="filter-category" onchange="filterAkinai()">
                    <option value="">すべてのカテゴリ</option>
                    <option value="item">物（備品・機器など）</option>
                    <option value="space">空間（間借り・スペース）</option>
                </select>
            </div>
            <div class="filter-group">
                <label>取引タイプ</label>
                <select id="filter-transaction" onchange="filterAkinai()">
                    <option value="">すべての取引タイプ</option>
                    <option value="sell">売ります</option>
                    <option value="give">あげます</option>
                    <option value="rent">貸します</option>
                </select>
            </div>
            <div class="filter-group">
                <label>フリーワード</label>
                <input type="text" id="filter-keyword" placeholder="店舗名、品目など" oninput="filterAkinai()">
            </div>
        </section>

        <!-- 一覧リスト -->
        <section class="job-list" id="akinai-list">
            {cards_html}
        </section>
    </main>

    <script>
        const menuButton = document.querySelector('.menu-button');
        const siteMenu = document.querySelector('#site-menu');
        if (menuButton) {{
            menuButton.addEventListener('click', () => {{
                const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
                menuButton.setAttribute('aria-expanded', String(!isOpen));
                siteMenu.hidden = isOpen;
            }});
        }}

        function filterAkinai() {{
            const category = document.getElementById('filter-category').value;
            const transaction = document.getElementById('filter-transaction').value;
            const keyword = document.getElementById('filter-keyword').value.toLowerCase();

            const cards = document.querySelectorAll('.akinai-card');

            cards.forEach(card => {{
                const cardCat = card.getAttribute('data-category') || '';
                const cardTrans = card.getAttribute('data-transaction') || '';
                const cardText = card.textContent.toLowerCase();

                let matchCat = !category || cardCat === category;
                let matchTrans = !transaction || cardTrans === transaction;
                let matchKeyword = !keyword || cardText.includes(keyword);

                if (matchCat && matchTrans && matchKeyword) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
