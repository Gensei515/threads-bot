import anthropic
import requests
import schedule
import time
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
THREADS_USER_ID = os.environ.get("THREADS_USER_ID")

def generate_post():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "ビジネス・マーケティングに関する投稿をThreads用に1つ作成してください。500文字以内で、読者が価値を感じる実践的な内容にしてください。ハッシュタグも3つ追加してください。投稿文のみ返答してください。"
            }
        ]
    )
    return message.content[0].text

def post_to_threads(text):
    # Step 1: コンテナ作成
    url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads"
    params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": THREADS_ACCESS_TOKEN
    }
    response = requests.post(url, params=params)
    container_id = response.json().get("id")
    
    if not container_id:
        print(f"エラー: {response.json()}")
        return
    
    # Step 2: 投稿
    publish_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish"
    publish_params = {
        "creation_id": container_id,
        "access_token": THREADS_ACCESS_TOKEN
    }
    publish_response = requests.post(publish_url, params=publish_params)
    print(f"投稿完了: {publish_response.json()}")

def job():
    print("投稿を生成中...")
    text = generate_post()
    print(f"生成された投稿: {text}")
    post_to_threads(text)

# 1日3回投稿（9時、13時、18時）
schedule.every().day.at("09:00").do(job)
schedule.every().day.at("13:00").do(job)
schedule.every().day.at("18:00").do(job)

print("Threads自動投稿Bot起動中...")
job()  # 起動時に1回実行
while True:
    schedule.run_pending()
    time.sleep(60)
