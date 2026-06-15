import anthropic
import requests
import os
import random

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
THREADS_USER_ID = os.environ.get("THREADS_USER_ID")

POST_TYPES = [
    """
【CV獲得型】SNS運用代行会社のサービス紹介投稿を作成してください。
以下のような構成で書いてください：
- 業界の「高すぎる相場」への問題提起
- 自社サービスの差別化（運用代行＋講座）
- 具体的な価格（月額2.6万円）
- 「お気軽にDMください」で締める
口語的でテンポよく、改行を多用してください。500文字以内。ハッシュタグ3つ。
""",
    """
【バズ狙い・尖った意見型】SNSマーケティングについて、業界の常識を覆すような尖った主張を投稿してください。
例：「フォロワー数は関係ない」「バズっても売上ゼロの会社がある理由」など
断言口調で、共感や反論を呼ぶような内容にしてください。500文字以内。ハッシュタグ3つ。
""",
    """
【教育型・保存されやすい】スタートアップや中小企業がSNS運用で直面するリアルな問題と解決策を投稿してください。
箇条書きや✅❌を使って見やすく構成してください。
「あるある」と共感されやすい内容で。500文字以内。ハッシュタグ3つ。
""",
    """
【問題提起型】「SNSをやらない企業のリスク」について、データや具体例を交えて警鐘を鳴らす投稿を作成してください。
「SNSはもはや名刺代わり」のような強いメッセージで始めてください。500文字以内。ハッシュタグ3つ。
""",
    """
【共感型・スタートアップ向け】スタートアップ創業期のSNS運用の悩みに寄り添い、解決策を提示する投稿を作成してください。
「わかる」「自分のことだ」と思われるような内容で。最後にDMを促す。500文字以内。ハッシュタグ3つ。
"""
]

def generate_post():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    post_type = random.choice(POST_TYPES)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""あなたはSNS運用代行会社のThreads担当者です。
以下の指示に従って投稿文を作成してください。

{post_type}

【重要なルール】
- 投稿文のみ返答（説明不要）
- 改行を多用してテンポよく
- 口語的でリアルな言葉を使う
- 業界用語より平易な言葉を優先
- 最後は行動を促す一言で締める"""
            }
        ]
    )
    return message.content[0].text

def post_to_threads(text):
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
    
    publish_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish"
    publish_params = {
        "creation_id": container_id,
        "access_token": THREADS_ACCESS_TOKEN
    }
    publish_response = requests.post(publish_url, params=publish_params)
    print(f"投稿完了: {publish_response.json()}")

print("投稿を生成中...")
text = generate_post()
print(f"生成された投稿:\n{text}")
post_to_threads(text)
