# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：第1回（素のLLM）とエージェントの回答の違い　第1回では、素のLLMが事前学習済みの知識を利用して回答するため、講座固有の情報については正確に回答できない場合があった。一方、第3回では、エージェントが search_glossary を使って講座の用語集を検索し、取得した情報を参照して回答できるようになった。これにより、モデルが事前に知らない講座固有の情報についても、外部データを根拠として回答できる仕組みになった。

- `--trace` で見えたツール呼び出し（ツール名と引数）：app/agent.py に agent.tool_plain(tools.make_quiz) を追加し、確認問題を生成するツールを登録した。--list-tools を実行し、search_glossary、get_lecture_summary、make_quiz の3つのツールが登録されていることを確認した。また、--trace を使って実行時のツール呼び出しを確認したところ、「第2回の内容から確認問題を1問出して」という質問に対して、次の呼び出しが行われた。[tool call] make_quiz({'lecture': 2})　この結果から、LLMが質問の内容に応じて make_quiz を選択し、対象の講義回を引数 lecture=2 として渡していることが確認できた。

- 1つの質問での LLM 呼び出し回数（`requests`）：「第2回の内容から確認問題を1問出して」と質問したところ、用語集から「Hugging Face Hub」が選ばれ、「Hugging Face Hubの意味は何ですか？」という確認問題が生成された。この実行では、以下の結果が得られた。LLMへのリクエスト数：requests=2　ツール呼び出し数：tool_calls=1　これは、最初のLLM呼び出しでツールの使用が選択され、プログラムがツールを実行した後、その結果を使ってLLMが最終回答を生成したことを示している。最後に uv run pytest -q を実行し、11件のテストがすべて成功したことを確認した。
- 追加したツールと、docstring に書いた説明：
追加したツール
def make_quiz(lecture: int) -> str:
    """指定した回の用語から1つを選び、確認問題と答えを返す。

    「第2回の確認問題を出して」のように、
    特定の回の復習問題や理解度確認の問題を求められたときに使う。
    lectureには対象となる講義の回数を整数で指定する。
    """
    glossary = load_glossary()

    # 指定した回に対応する用語を集める
    terms = [
        entry for entry in glossary
        if entry["lecture"] == lecture
    ]

    # 対応する用語がない場合もエラーにしない
    if not terms:
        return f"第{lecture}回の確認問題に使える用語はありません。"

    # 用語をランダムに1つ選ぶ
    selected = random.choice(terms)

    # 問題と答えを作る
    quiz = {
        "question": f"「{selected['term']}」の意味は？",
        "answer": selected["definition"],
    }

    return json.dumps(quiz, ensure_ascii=False)

docstring に書いた説明：確認問題や復習問題を求められたときに使用するツールであることを説明した。また、lecture 引数には対象となる講義の回数を整数で指定することを明記した。
エージェントへの登録と指示　app/agent.py に以下を追加した。
agent.tool_plain(tools.make_quiz)
また、エージェントの指示（INSTRUCTIONS）に以下を追加した。
- 確認問題や復習問題を求められたら make_quiz を使う。
これにより、LLMがユーザーの質問に応じて make_quiz を選択し、必要な引数を指定して呼び出せるようにした。

## 宿題

- 取り組んだレベル：基礎

- やったこと：変更した内容　app/tools.pyのsearch_glossary関数のdocstringについて、「queryには調べたい用語を1つだけ入れる」という説明を、「複数の用語について質問された場合は、queryにそれらの用語をまとめて指定してよい」という説明に変更した。関数本体は変更せず、docstringのみを変更した。

- 結果：比較した質問
「LoRAとQLoRAの違いは？
実行結果
元のdocstringでは、search_glossaryが2回呼び出され、それぞれquery='LoRA'、query='QLoRA'が指定された。LLMへのリクエスト数は2回、ツール呼び出し数は2回だった。一方、変更後のdocstringでは、search_glossaryが1回だけ呼び出され、query='LoRA QLoRA'が指定された。LLMへのリクエスト数は2回、ツール呼び出し数は1回だった。両条件とも、LoRAとQLoRAの違いについて適切な回答が生成された。さらに、search_glossary('LoRA QLoRA')を直接実行したところ、LoRAとQLoRAの両方の定義が取得できることを確認した。

- 気づき・疑問：docstringの説明を変更したことで、LLMがツールに渡す引数とツール呼び出し回数が変化した。この結果から、ツールのdocstringがLLMのツール使用方法に影響することが確認できた。今回の質問では、複数用語をまとめて指定することで、必要な情報を取得したままツール呼び出し回数を2回から1回に減らすことができた。一方、LLMへのリクエスト数は変化しなかった。このことから、ツールの機能を適切に説明するdocstringを設計することで、エージェントのツール利用を効率化できる可能性があると考えられる。
