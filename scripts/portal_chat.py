import os
import json

# 記憶を保存するファイルのパス（tsunagaroフォルダの中に保存します）
MEMORY_FILE = os.path.expanduser("~/Desktop/tsunagaro/data/chat_memory.json")
PROMPT_FILE = os.path.expanduser("~/Desktop/tsunagaro/tsunagaro_ai_prompt.txt")

def load_memory():
    """過去の会話の記憶をロードする"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_memory(memory):
    """会話の記憶をファイルに上書き保存する"""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def load_system_prompt():
    """最初に読ませる設定プロンプトを読み込む"""
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "あなたは「つながろ」の開発アシスタントです。"

def main():
    print("=" * 50)
    print(" 🚀 「つながろ」専用 AIチャットボット起動中...")
    print("=" * 50)

    # 記憶とプロンプトの読み込み
    memory = load_memory()
    system_prompt = load_system_prompt()

    if not memory:
        # 初回起動時はシステムプロンプトを最初の記憶としてインプット
        memory.append({"role": "system", "content": system_prompt})
        print("💡 [システム設定] 初回プロンプトを脳内にロードしました。")
    else:
        print(f"🔄 [システム設定] 過去の記憶（{len(memory)}件のやり取り）を復元しました！")

    print("\n（終了したいときは 'exit' または 'quit' と入力してください）\n")

    while True:
        try:
            user_input = input("あなた: ")
            if user_input.lower() in ["exit", "quit"]:
                print("👋 チャットを終了します。記憶は自動保存されました。")
                break
            
            if not user_input.strip():
                continue

            # ユーザーの発言を記憶に追加
            memory.append({"role": "user", "content": user_input})

            # ----------------------------------------------------
            # ここに実際のAI（APIなど）の返答処理が入ります
            # ----------------------------------------------------
            # 例（ダミー応答）:
            ai_response = f"（つながろAIの応答シミュレーション）「{user_input}」ですね。了解です！"
            
            print(f"AI: {ai_response}\n")

            # AIの返答も記憶に追加
            memory.append({"role": "assistant", "content": ai_response})

            # 毎回自動でファイルに保存する
            save_memory(memory)

        except KeyboardInterrupt:
            print("\n👋 強制終了しました。記憶は保存されています。")
            break

if __name__ == "__main__":
    main()
