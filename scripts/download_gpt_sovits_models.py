import os
from huggingface_hub import hf_hub_download

def download_pretrained_models(target_dir: str = "backend/GPT_SoVITS/GPT_SoVITS/pretrained_models"):
    """
    GPT-SoVITS 事前学習モデル重みおよび設定ファイル (preprocessor_config.json等) をダウンロードする。
    """
    os.makedirs(target_dir, exist_ok=True)
    repo_id = "lj1995/GPT-SoVITS"

    print(f"GPT-SoVITS 事前学習モデル設定ファイルを補完中... ({target_dir})")

    try:
        # chinese-hubert-base 設定ファイル群
        hubert_files = ["config.json", "preprocessor_config.json", "pytorch_model.bin"]
        for f in hubert_files:
            rel_path = f"chinese-hubert-base/{f}"
            print(f"-> {rel_path} を取得中...")
            try:
                hf_hub_download(repo_id=repo_id, filename=rel_path, local_dir=target_dir)
            except Exception as ex:
                print(f"警告: {rel_path} の取得スキップ: {ex}")

        # chinese-roberta-wwm-ext-large 設定ファイル群
        roberta_files = ["config.json", "pytorch_model.bin", "tokenizer.json", "vocab.txt"]
        for f in roberta_files:
            rel_path = f"chinese-roberta-wwm-ext-large/{f}"
            print(f"-> {rel_path} を取得中...")
            try:
                hf_hub_download(repo_id=repo_id, filename=rel_path, local_dir=target_dir)
            except Exception as ex:
                print(f"警告: {rel_path} の取得スキップ: {ex}")

        print("\n==================================================")
        print("設定ファイルのダウンロード・補完が完了しました！")
        print("==================================================")

    except Exception as e:
        print(f"モデルダウンロード中にエラーが発生しました: {e}")
        raise e

if __name__ == "__main__":
    download_pretrained_models()
