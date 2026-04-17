import pandas as pd
import os
import logging
from text_processing import fix_contents

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def transform_silver_to_gold_pandas():
    minio_options = {
        "key": "minioadmin",
        "secret": "minioadmin",
        "client_kwargs": {
            "endpoint_url": "http://localhost:9000"
        }
    }

    input_folder = "s3://silver/readtoolead_processed/processed/"
    output_dir = "/home/hoangduy/PycharmProjects/hus-ai-translator/data/gold/mtet_ready/"

    try:
        logger.info(f"Loading data: {input_folder}")

        df = pd.read_parquet(input_folder, engine='pyarrow', storage_options=minio_options)
        def safe_fix(text):
            try:
                if text is None or str(text).strip() == "":
                    return ""
                return fix_contents(str(text))
            except Exception:
                return ""

        #Xu ly va gan tag
        df['en_gold'] = df['English'].apply(safe_fix) + r" \ news"
        df['vi_gold'] = df['Vietnamese'].apply(safe_fix) + r" \ tin tức"

        # Loc loi phat sinh
        df = df[df['en_gold'].str.len() > 10]
        logger.info(f"Số lượng câu sạch sau khi chuẩn hóa: {len(df)}")

        logger.info("Split Train/Dev...")
        df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
        split_idx = int(len(df_shuffled) * 0.95)

        train_df = df_shuffled.iloc[:split_idx]
        dev_df = df_shuffled.iloc[split_idx:]

        os.makedirs(output_dir, exist_ok=True)

        def save_txt(subset, prefix):
            en_path = os.path.join(output_dir, f"{prefix}.en")
            vi_path = os.path.join(output_dir, f"{prefix}.vi")

            with open(en_path, "w", encoding="utf-8") as f:
                f.write("\n".join(subset['en_gold'].astype(str)))
            with open(vi_path, "w", encoding="utf-8") as f:
                f.write("\n".join(subset['vi_gold'].astype(str)))

            logger.info(f"Saved {len(subset)} sentences into {prefix}")

        save_txt(train_df, "train")
        save_txt(dev_df, "dev")

        logger.info("----COMPLETE----")

    except Exception as e:
        logger.error(f"Exception: {str(e)}")
