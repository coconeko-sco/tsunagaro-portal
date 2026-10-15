import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
MASTER_JSON_PATH = ROOT / "data" / "stores_master.json"

JST = timezone(timedelta(hours=9))

def is_closed_day(closed_days, now_jst):
    if not closed_days:
        return False
    weekday_str = now_jst.strftime("%a") # Mon, Tue, Wed...
    week_of_month = (now_jst.day - 1) // 7 + 1
     ordinal = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}.get(week_of_month, "")
    nth_weekday = f"{ordinal}_{weekday_str}"
    return (weekday_str in closed_days) or (nth_weekday in closed_days)

def is_within_hours(hours_list, now_jst):
    if not hours_list:
        return True
    now_hm = now_jst.strftime("%H:%M")
    for period in hours_list:
        if "-" in period:
            start_hm, end_hm = period.split("-", 1)
            if start_hm.strip() <= now_hm < end_hm.strip():
                return True
    return False

def main():
    if not MASTER_JSON_PATH.exists():
        sys.exit(0)

    with open(MASTER_JSON_PATH, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    stores = master_data.get("stores", {})
    now_utc = datetime.now(timezone.utc)
    now_jst = datetime.now(JST)
    updated_count = 0

    for store_id, store in stores.items():
        current = store.get("current")
        if not current:
            continue

        action_key = current.get("action_key", "default")
        if action_key == "default":
            continue

        reset_needed = False
        expires_at_str = current.get("expires_at")

        # 1. タイマー期限切れチェック
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
                if now_utc >= expires_at:
                    reset_needed = True
            except Exception:
                pass

        # 2. 営業時間・定休日のチェック
        closed_days = store.get("closed_days", [])
        hours_list = store.get("hours", [])

        if is_closed_day(closed_days, now_jst):
            # 定休日はすべてのボタン効果をリセット
            reset_needed = True
        elif action_key in ["button_a", "button_b"]:
            # A・Bボタン（営業中・待ち時間）は営業時間内のみ有効（中休みや閉店後は自動リセット）
            if hours_list and not is_within_hours(hours_list, now_jst):
                reset_needed = True
        elif action_key == "button_c":
            # Cボタン（本日終了・早じまい）は、最後の営業時間が終わる前（または日付が変わった後）で営業時間外なら自動判定へ戻す
            if hours_list:
                first_start = hours_list[0].split("-")[0].strip()
                last_end = hours_list[-1].split("-")[1].strip()
                now_hm = now_jst.strftime("%H:%M")
                # 朝のオープン前（0:00〜オープン時刻）になったら前日の「本日終了」ボタンを解除して「準備中」に戻す
                if now_hm < first_start or now_hm >= last_end:
                    reset_needed = True

        if reset_needed:
            store["current"] = {
                "action_key": "default",
                "status": "",
                "message": "",
                "color": "",
                "expires_at": None
            }
            updated_count += 1
            print(f"[{store_id}] 自動判定モード（default）にリセットしました。")

    if updated_count > 0:
        with open(MASTER_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
