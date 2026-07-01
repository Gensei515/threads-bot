import anthropic
import requests
import os
import random

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
THREADS_USER_ID = os.environ.get("THREADS_USER_ID")

POST_TYPES = [
    """
【CV獲得型】以下の構成でThreads投稿を作成してください。

テーマ：SNS運用代行の価格と弊社サービスの差別化
ターゲット：SNSを始めたい中小企業・スタートアップ経営者
伝えたい結論：月2.6万円で運用代行＋講座＋300本以上のノウハウ動画が使える

最初の1〜3行は、思わず続きを読みたくなる強いフックにしてください。
難しい言葉は使わず、友達に話すような口調で500〜800文字程度にまとめてください。
最後は押し売り感を出さず「気になった方はDMください」で締めてください。
同じ文末を連続させず、短い文章と長い文章を混ぜてください。
AIが書いたような不自然な表現は避けてください。
""",
    """
【バズ狙い・尖った意見型】以下の構成でThreads投稿を作成してください。

テーマ：SNS運用でよくある間違い、または業界の常識を覆す主張
ターゲット：SNS運用に悩む経営者・マーケター
伝えたい結論：フォロワー数より質、バズより信頼、など逆張りの主張

最初の1行で「え？」と思わせる意外な一言から始めてください。
断言口調で、共感や反論を呼ぶような内容にしてください。
具体的な数字や事例を入れてください。
500文字以内。ハッシュタグ3つ。
""",
    """
【問題提起型】以下の構成でThreads投稿を作成してください。

テーマ：SNSをやっていない企業が失っているもの
ターゲット：SNSに消極的な中小企業経営者
伝えたい結論：SNSは今や企業の名刺。やらないことのリスクは大きい

✅❌を使って対比を見せてください。
危機感を煽りすぎず、でも行動したくなる内容にしてください。
最後にプロフィールを見たくなる自然な一文を入れてください。
500文字以内。ハッシュタグ3つ。
""",
    """
【共感・ストーリー型】以下の構成でThreads投稿を作成してください。

テーマ：スタートアップ・中小企業がSNS運用で直面するリアルな悩み
ターゲット：SNSを始めたいけど何から手をつければいいか分からない経営者
伝えたい結論：正しい順序で始めれば、SNSは必ず結果が出る

「私も最初は〇〇だった」→「実際に試したところ〇〇になった」→「だから今は〇〇している」
という流れで書いてください。
自慢話ではなく、読者が自分にも当てはめられる内容にしてください。
最後はDMを促す自然な一言で。500〜700文字。ハッシュタグ3つ。
""",
    """
【教育・保存型】以下の構成でThreads投稿を作成してください。

テーマ：SNS運用で今すぐ使える具体的なノウハウ（投稿時間・フック・構成など）
ターゲット：SNSを自分で運用している経営者・担当者
伝えたい結論：小さな工夫で閲覧数・いいね数は大きく変わる

箇条書きや番号リストを使って見やすくしてください。
「保存して後で見返したい」と思われる実践的な内容にしてください。
最後に「他にも知りたい方はDMください」で締めてください。
500文字以内。ハッシュタグ3つ。
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
実際に人間が書いたような自然な投稿を作成してください。

{post_type}

【絶対に守るルール】
- 投稿文のみ返答（説明・前置き不要）
- AIっぽい綺麗すぎる表現は使わない
- 同じ文末（〜です、〜ます）を3回以上連続させない
- 短い文と長い文を混ぜてテンポを作る
- 感情や本音を少し入れる
- 押し売り感を出さない"""
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
