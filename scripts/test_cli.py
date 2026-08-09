import os
import sys
import argparse

# backend ディレクトリを sys.path に追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.tts import ChatterboxAdapter

def main():
    parser = argparse.ArgumentParser(description="MyVoice Speech - Phase 1 CLI 音声生成テストスクリプト")
    parser.add_argument("--ref", type=str, default="samples/reference.wav", help="参照音声WAVファイルのパス")
    parser.add_argument("--text", type=str, default="本日はご結婚おめでとうございます。新郎の父でございます。二人の新しい門出を心よりお祝い申し上げます。", help="合成する日本語スピーチ原稿テキスト")
    parser.add_argument("--output", type=str, default="backend/outputs/test_output.wav", help="出力先WAVファイルのパス")
    args = parser.parse_args()

    print("==================================================")
    print("MyVoice Speech - Phase 1 CLI 音声生成テスト開始")
    print("==================================================")
    print(f"参照音声: {args.ref}")
    print(f"入力テキスト: {args.text}")
    print(f"出力先: {args.output}")
    print("--------------------------------------------------")

    # 1. 参照音声の存在チェック
    if not os.path.exists(args.ref):
        print(f"エラー: 参照音声ファイル {args.ref} が存在しません。")
        sys.exit(1)

    # 2. アダプターの初期化と音声生成
    try:
        adapter = ChatterboxAdapter()
        output_file = adapter.generate(
            text=args.text,
            reference_audio_path=args.ref,
            output_path=args.output,
            language="ja"
        )

        # 3. 成功検証
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            file_size_kb = os.path.getsize(output_file) / 1024.0
            print("--------------------------------------------------")
            print("【Phase 1 成功】日本語音声が正常に生成されました！")
            print(f"生成ファイル: {output_file}")
            print(f"ファイルサイズ: {file_size_kb:.2f} KB")
            print("==================================================")
        else:
            print("エラー: 音声ファイルが空または正常に生成されませんでした。")
            sys.exit(1)

    except Exception as e:
        print(f"音声生成中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
