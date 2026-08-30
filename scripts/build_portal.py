import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "tsunagaro_data.json")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "index.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")

def main():
    print("🚀 「つながろ」ポータルのビルドを開始します...")

    # 1. JSON読み込み
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. テンプレート読み込み
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        html_template = f.read()

    # 3. カードのHTMLを動的に組み立てる（確実に表示される画像URLを使用）
    cards_html = ""
    for i, card in enumerate(data["cards"]):
        image_url = card.get("image_url", "")
        if not image_url:
            if i == 0:
                # 1番目（カツ丼・丼ものに最も近い高画質フリー素材）
                image_url = "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80"
            elif i == 1:
                # 2番目（イベント）
                image_url = "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=600&auto=format&fit=crop&q=80"
            elif i == 2:
                # 3番目（子育て）
                image_url = "https://images.unsplash.com/photo-1526232761682-d26e03ac148e?w=600&auto=format&fit=crop&q=80"
            else:
                # 4番目（ビアガーデン）
                image_url = "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=600&auto=format&fit=crop&q=80"

        cards_html += f"""
            <div class="card">
                <img src="{image_url}" alt="" class="card-image">
                <div class="card-body">
                    <div class="card-header">
                        <span class="category-tag">{card["category"]}</span>
                        <span class="badge {card["status"]}">{card["status_label"]}</span>
                    </div>
                    <h3>{card["title"]}</h3>
                    <p>{card["description"]}</p>
                    <div class="card-footer">
                        <span>📍 {card["location"]}</span>
                        <span>🕒 {card["date"]}</span>
                    </div>
                </div>
            </div>
        """

    # 4. テンプレートのプレースホルダーを置き換え
    hot = data["hot_topics"]
    final_html = html_template.replace("{{HOT_TITLE}}", hot.get("title", ""))
    final_html = final_html.replace("{{HOT_DESCRIPTION}}", hot["description"])
    final_html = final_html.replace("{{HOT_UPDATED}}", hot["updated_at"])
    final_html = final_html.replace("{{CARD_LIST_HTML}}", cards_html)

    # 5. 出力
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✨ ビルド成功！ポータルサイトが更新されました: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
