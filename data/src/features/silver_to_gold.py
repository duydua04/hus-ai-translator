import pandas as pd
import logging
from text_processing import fix_contents

logger = logging.getLogger(__name__)


def transform_silver_to_gold(df: pd.DataFrame, use_tags: bool = True) -> pd.DataFrame:
    logger.info(f"Tiến hành chuẩn hóa")

    def safe_fix(text):
        try:
            if text is None or str(text).strip() == "":
                return ""
            return fix_contents(str(text))
        except Exception:
            return ""

    df_processed = df.copy()

    if use_tags:
        df_processed['en_gold'] = df_processed['English'].apply(safe_fix) + r" \ news"
        df_processed['vi_gold'] = df_processed['Vietnamese'].apply(safe_fix) + r" \ tin tức"
    else:
        df_processed['en_gold'] = df_processed['English'].apply(safe_fix)
        df_processed['vi_gold'] = df_processed['Vietnamese'].apply(safe_fix)

    df_processed = df_processed[
        (df_processed['en_gold'].str.len() > 10) &
        (df_processed['vi_gold'].str.len() > 10)
        ].reset_index(drop=True)

    df_processed.insert(0, 'id', range(1, len(df_processed) + 1))

    logger.info(f"Hoàn tất xử lý.")
    return df_processed