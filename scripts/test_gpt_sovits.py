import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.tts import GPTSoVITSAdapter

def main():
    parser = argparse.ArgumentParser(description="MyVoice Speech - GPT-SoVITS ゼロショット音声合成＆音質最適化テスト")
    parser.add_argument("--ref", type=str, default="samples/my_voice.wav", help="参照音声WAVパス")
    parser.add_argument("--text", type=str, default="本日はご結婚おめでとうございます。新郎の父でございます。二人の新しい門出を心よりお祝い申し上げます。", help="合成テキスト")
    parser.add_argument("--output", type=str, default="backend/outputs/real_gpt_sovits_speech.wav", help="出力WAVパス")
    parser.add_argument("--top_k", type=int, default=15, help="top_k (デフォルト: 15)")
    parser.add_argument("--top_p", type=float, default=1.0, help="top_p (デフォルト: 1.0)")
    parser.add_argument("--temperature", type=float, default=0.7, help="temperature (デフォルト: 0.7)")
    args = parser.parse_args()

    ref_audio = args.ref
    if not os.path.exists(ref_audio):
        print(f"エラー: 参照音声 {ref_audio} が見つかりません。")
        sys.exit(1)

    print("==================================================")
    print("MyVoice Speech - GPT-SoVITS ゼロショットクローン音声生成（VAD+Whisper自動最適化）")
    print("==================================================")

    adapter = GPTSoVITSAdapter()
    try:
        output_file = adapter.generate(
            text=args.text,
            reference_audio_path=ref_audio,
            output_path=args.output,
            language="ja",
            top_k=args.top_k,
            top_p=args.top_p,
            temperature=args.temperature
        )

        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            file_size_kb = os.path.getsize(output_file) / 1024.0
            print("--------------------------------------------------")
            print("【GPT-SoVITS 生成成功】高品質な日本語クローン音声が生成されました！")
            print(f"生成ファイル: {output_file}")
            print(f"ファイルサイズ: {file_size_kb:.2f} KB")
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

