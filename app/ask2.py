"""会話履歴を保持しながらLLMに質問するスクリプト。"""

from google import genai
from google.genai import errors
from google.genai import types

from app.config import MODEL, api_error_message, get_api_key


def chat_loop() -> None:
    client = genai.Client(api_key=get_api_key())

    chat = client.chats.create(
        model=MODEL,
    )

    print(f"[model] {MODEL}")
    print("会話を開始します。終了するには exit と入力してください。\n")

    while True:
        question = input("[質問] ").strip()

        if question.lower() in {"exit", "quit"}:
            print("会話を終了します。")
            break

        if not question:
            continue

        response = chat.send_message(question)

        usage = response.usage_metadata
        if usage is not None:
            print(f"[入力トークン数] {usage.prompt_token_count}")
            print(f"[出力トークン数] {usage.candidates_token_count}")

        print(f"[回答] {response.text}\n")


def main() -> None:
    try:
        chat_loop()
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
