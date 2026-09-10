import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "jobs.json"
OUTPUT_PATH = ROOT / "jobs" / "jobs.html"

def load_jobs():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def render_job_card(job):
    b = job["basic_info"]
    w = job["work_conditions"]
    e = job["environment"]
    t = job["tags"]

    all_tags = []
    for category_tags in t.values():
        all_tags.extend(category_tags)

    tags_html = "".join([f'<span class="job-tag">{tag}</span>' for tag in all_tags])
    photos_html = "".join([f'<img src="{p}" alt="{b["store_name"]}" loading="lazy">' for p in e["photos"]])

    return f"""
    <article class="job-card" data-area="{b["area"]}" data-employment="{b["employment_type"]}" data-category="{b["category"]}" id="{job["id"]}">
        <div class="job-header">
            <div class="job-meta-row">
                <span class="category-tag">{b["category"]}</span>
                <span class="employment-badge">{b["employment_type"]}</span>
                <span class="area-badge">📍 {b["area"]}</span>
            </div>
            <h2>{b["title"]}</h2>
            <div class="store-info-bar">
                <strong>{b["store_name"]} ({b["branch_name"]})</strong>
                <span>{b["address"]}</span>
            </div>
        </div>

        <div class="job-body-grid">
            <div class="job-photos">
                {photos_html}
            </div>
            <div class="job-details-list">
                <div class="salary-box">
                    <span class="salary-label">{b["salary"]["type"]}</span>
                    <span class="salary-amount">¥{b["salary"]["amount"]:,}</span>
                    <p class="salary-detail">{b["salary"]["detail"]}</p>
                </div>
                
                <table class="job-table">
                    <tr><th>勤務時間</th><td>{w["working_hours"]}</td></tr>
                    <tr><th>シフト</th><td>{w["shift_detail"]}</td></tr>
                    <tr><th>休日・休暇</th><td>{w["holidays"]}</td></tr>
                    <tr><th>アクセス</th><td>{e["access"]}</td></tr>
                    <tr><th>連絡推奨時間</th><td class="highlight-time">✅ {e["store_call_hours"]["recommended_time"]}</td></tr>
                    <tr><th>避けてほしい時間</th><td class="muted-time">❌ {e["store_call_hours"]["avoid_time"]}</td></tr>
                </table>

                <div class="job-tags-grid">
                    {tags_html}
                </div>
            </div>
        </div>

        <div class="job-footer-action">
            <button class="toggle-apply-btn" type="button" onclick="toggleApplyForm('{job["id"]}')">
                📝 30秒カンタン応募フォームを開く
            </button>
        </div>

        <div class="job-apply-section" id="form-{job["id"]}" style="display: none;">
            <h3>30秒カンタン応募フォーム（{b["store_name"]}）</h3>
            <p class="apply-lead">店主へ直接つながるクリーンな応募フォームです。</p>
            <form class="quick-apply-form" onsubmit="handleApply(event, '{job["id"]}')">
                <input type="hidden" name="job_id" value="{job["id"]}">
                
                <div class="form-group">
                    <label>お名前（ふりがな） <span class="required">必須</span></label>
                    <input type="text" name="name" placeholder="例：山田 太郎（やまだ たろう）" required>
                </div>

                <div class="form-group">
                    <label>年代 <span class="required">必須</span></label>
                    <select name="generation" required>
                        <option value="">選択してください</option>
                        <option value="20代">20代</option>
                        <option value="30代">30代</option>
                        <option value="40代">40代</option>
                        <option value="50代以上">50代以上</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>連絡先（電話番号またはメールアドレス） <span class="required">必須</span></label>
                    <input type="text" name="contact" placeholder="例：090-XXXX-XXXX" required>
                </div>

                <div class="form-group">
                    <label>雇用形態の希望 <span class="required">必須</span></label>
                    <div class="radio-group">
                        <label><input type="radio" name="pref_employment" value="正社員" required> 正社員</label>
                        <label><input type="radio" name="pref_employment" value="パート・アルバイト" required> パート・アルバイト</label>
                    </div>
                </div>

                <div class="form-group">
                    <label>【現場配慮】連絡希望時間帯 <span class="required">必須</span></label>
                    <div class="radio-group vertical">
                        <label><input type="radio" name="contact_time" value="09:00〜12:00" required> 09:00〜12:00</label>
                        <label><input type="radio" name="contact_time" value="12:00〜15:00" required> 12:00〜15:00</label>
                        <label><input type="radio" name="contact_time" value="15:00〜18:00（ピーク外推奨）" required> 15:00〜18:00（ピーク外推奨）</label>
                        <label><input type="radio" name="contact_time" value="18:00以降" required> 18:00以降</label>
                    </div>
                </div>

                <div class="form-group">
                    <label>希望シフト・一言メモ（任意）</label>
                    <textarea name="memo" placeholder="例：Wワーク希望、週3日〜働きたいです"></textarea>
                </div>

                <button type="submit" class="submit-btn">規約に同意して送信する（30秒）</button>
            </form>
        </div>
    </article>
    """

def main():
    jobs = load_jobs()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cards_html = "".join([render_job_card(job) for job in jobs])

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
    <title>つながろ求人 | 地域密着の求人ポータル</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header class="topbar">
        <div class="topbar-inner">
            <div class="brand-group">
                <div class="brand">つながろ求人</div>
                <span class="coming-soon">Coming soon...</span>
            </div>
            <button class="menu-button" type="button" aria-label="メニューを開く" aria-expanded="false" aria-controls="site-menu">
                <span></span><span></span><span></span>
            </button>
            <nav class="menu-panel" id="site-menu" hidden>
                <a href="../index.html">TOP</a>
                <a href="./jobs.html">求人一覧</a>
            </nav>
        </div>
    </header>

    <main class="container job-portal-container">
        <!-- 検索・フィルターバー -->
        <section class="filter-section">
            <div class="filter-group">
                <label>エリア</label>
                <select id="filter-area" onchange="filterJobs()">
                    <option value="">すべてのエリア</option>
                    <option value="飯塚市">飯塚市</option>
                    <option value="田川市">田川市</option>
                    <option value="直方市">直方市</option>
                </select>
            </div>
            <div class="filter-group">
                <label>雇用形態</label>
                <select id="filter-employment" onchange="filterJobs()">
                    <option value="">すべての雇用形態</option>
                    <option value="正社員">正社員</option>
                    <option value="パート・アルバイト">パート・アルバイト</option>
                </select>
            </div>
            <div class="filter-group">
                <label>フリーワード</label>
                <input type="text" id="filter-keyword" placeholder="職種、店舗名など" oninput="filterJobs()">
            </div>
        </section>

        <!-- 求人一覧リスト -->
        <section class="job-list" id="job-list">
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

        function toggleApplyForm(jobId) {{
            const formDiv = document.getElementById('form-' + jobId);
            if (formDiv.style.display === 'none') {{
                formDiv.style.display = 'block';
                formDiv.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }} else {{
                formDiv.style.display = 'none';
            }}
        }}

        function handleApply(event, jobId) {{
            event.preventDefault();
            alert('ご応募ありがとうございます！店舗へ応募通知が送信されました。');
            event.target.reset();
            document.getElementById('form-' + jobId).style.display = 'none';
        }}

        function filterJobs() {{
            const area = document.getElementById('filter-area').value;
            const employment = document.getElementById('filter-employment').value;
            const keyword = document.getElementById('filter-keyword').value.toLowerCase();

            const cards = document.querySelectorAll('.job-card');

            cards.forEach(card => {{
                const cardArea = card.getAttribute('data-area') || '';
                const cardEmployment = card.getAttribute('data-employment') || '';
                const cardText = card.textContent.toLowerCase();

                let matchArea = !area || cardArea.includes(area);
                let matchEmployment = !employment || cardEmployment === employment;
                let matchKeyword = !keyword || cardText.includes(keyword);

                if (matchArea && matchEmployment && matchKeyword) {{
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
