import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.tts import GPTSoVITSAdapter

def main():
    parser = argparse.ArgumentParser(description="MyVoice Speech - GPT-SoVITS 日本語音声クローン生成テスト")
    parser.add_argument("--ref", type=str, default="samples/my_voice.wav", help="参照音声WAVパス")
    parser.add_argument("--text", type=str, default="本日は、ご結婚、おめでとうございます。新郎の父でございます。二人の新しい門出を、心よりお祝い申し上げます。", help="合成テキスト")
    parser.add_argument("--output", type=str, default="backend/outputs/gpt_sovits_father_speech.wav", help="出力WAVパス")
    args = parser.parse_args()

    ref_audio = args.ref
    if not os.path.exists(ref_audio):
        print(f"エラー: 参照音声 {ref_audio} が見つかりません。")
        sys.exit(1)

    print("==================================================")
    print("MyVoice Speech - GPT-SoVITS ゼロショットクローンテスト開始")
    print("==================================================")
    print(f"参照音声: {ref_audio}")
    print(f"入力テキスト: {args.text}")
    print(f"出力先: {args.output}")
    print("--------------------------------------------------")

    adapter = GPTSoVITSAdapter()
    try:
        output_file = adapter.generate(
            text=args.text,
            reference_audio_path=ref_audio,
            output_path=args.output,
            language="ja",
            speed_factor=0.85
        )

        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print("--------------------------------------------------")
            print("【GPT-SoVITS 生成成功】クリアな日本語クローン音声が作成されました！")
            print(f"生成ファイル: {output_file}")
            print(f"ファイルサイズ: {os.path.getsize(output_file)/1024.0:.2f} KB")
            print("==================================================")
        else:
            print("エラー: 音声ファイルの生成に失敗しました。")
            sys.exit(1)

    except Exception as e:
        print(f"GPT-SoVITS 生成中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
