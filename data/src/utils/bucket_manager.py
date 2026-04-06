from configs.bucket_config import get_bucket_config
import pandas as pd
from datetime import datetime
import s3fs

class BucketManager:
    def __init__(self):
        self.config = get_bucket_config()
        self.storage_options = self.config.storage_options
        self.fs = s3fs.S3FileSystem(**self.storage_options)


    def save_dataframe(self, df : pd.DataFrame, bucket : str, folder : str,
                       file_name: str = None,
                       file_format = "json",
                       partition_cols: list = None,
                       **kwargs):
        if df is None or df.empty:
            print(f"DataFrame rỗng: Bỏ qua upload lên bucket {bucket}")
            return
        
        # Chuẩn hóa format file format
        file_format = file_format.lower()
        if file_format not in ["parquet","json", "csv"]:
            raise ValueError(f"Định dạng file không được hỗ trợ: {file_format}. Hỗ trợ: json, csv")
        
        # Tạo tên file nếu không được cung cấp
        if file_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"data_{timestamp}.{file_format}"

        full_path = f"s3://{bucket}/{folder}/{file_name}.{file_format}"

        # Đặc biệt: Nếu Parquet có Partition, path là folder cha, không phải file
        if file_format == 'parquet' and partition_cols:
            full_path = f"s3://{bucket}/{folder}"

        try:
            print(f"[{file_format.upper()}] Uploading {len(df)} rows to: {full_path}...")

            if file_format == 'parquet':
                df.to_parquet(
                    path=full_path,
                    storage_options=self.storage_options,
                    index=False,
                    engine='pyarrow',
                    compression='snappy',
                    partition_cols=partition_cols,
                    **kwargs
                )

            elif file_format == 'csv':
                df.to_csv(
                    path_or_buf=full_path,
                    storage_options=self.storage_options,
                    index=False,
                    encoding='utf-8-sig',
                    **kwargs
                )

            elif file_format == 'json':
                df.to_json(
                    path_or_buf=full_path,
                    storage_options=self.storage_options,
                    orient='records',
                    lines=True,
                    force_ascii=False,
                    **kwargs
                )

            print(f"✅ Upload thành công!")

        except Exception as e:
            print(f"❌ Lỗi Upload Bucket ({file_format}): {e}")
            raise e

    def read_dataframe(self, bucket: str, folder: str, file_name: str, file_format: str = 'parquet') -> pd.DataFrame:
        """
        Đọc file từ Bucket về DataFrame.
        """
        full_path = f"s3://{bucket}/{folder}/{file_name}.{file_format}"
        print(f"⬇️ Reading from: {full_path}")

        try:
            if file_format == 'parquet':
                return pd.read_parquet(full_path, storage_options=self.storage_options)
            elif file_format == 'csv':
                return pd.read_csv(full_path, storage_options=self.storage_options)
            elif file_format == 'json':
                return pd.read_json(full_path, storage_options=self.storage_options, lines=True)
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ Lỗi Read Bucket: {e}")
            return pd.DataFrame()