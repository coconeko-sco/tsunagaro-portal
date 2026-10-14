import json
import sys
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
MASTER_JSON_PATH = ROOT / "data" / "stores_master.json"

def main():
    if not MASTER_JSON_PATH.exists():
        print("マスターJSONが見つかりません")
        sys.exit(0)

    with open(MASTER_JSON_PATH, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    stores = master_data.get("stores", {})
    now_utc = datetime.now(timezone.utc)
    updated_count = 0

    for store_id, store in stores.items():
        current = store.get("current")
        if not current:
            continue

        expires_at_str = current.get("expires_at")
        if not expires_at_str:
            continue

        try:
            # ISO 8601形式（例: 2026-10-15T12:00:00+09:00 や Z）をパースして現在時刻と比較
            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            if now_utc >= expires_at:
                # 期限切れの場合、actions.default の内容に戻す
                default_action = store.get("actions", {}).get("default", {})
                if default_action:
                    store["current"] = {
                        "action_key": "default",
                        "status": default_action.get("status", "営業案内"),
                        "message": default_action.get("message", ""),
                        "color": default_action.get("color", "#7f8c8d"),
                        "expires_at": None
                    }
                    updated_count += 1
                    print(f"[{store_id}] 期限切れのためデフォルトに戻しました。")
        except Exception as e:
            print(f"[{store_id}] 日付の解析エラー: {e}")

    # 変更があった場合のみJSONを上書き保存（無駄な書き込み防止）
    if updated_count > 0:
        with open(MASTER_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        print(f"合計 {updated_count} 件の店舗ステータスをリセットしました。")
    else:
        print("期限切れの店舗はありませんでした。")

if __name__ == "__main__":
    main()
