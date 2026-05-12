import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, trim, size, split

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def transform_bronze_to_silver(spark: SparkSession, input_path: str) -> DataFrame:
    """
    Xu ly du lieu tu Bronze len Silver.
    """
    logger.info(f"Đang đọc dữ liệu Bronze từ: {input_path}")

    df = spark.read \
        .option("inferSchema", True) \
        .option("recursiveFileLookup", "true") \
        .json(input_path)

    df = df.filter(
        col("English").isNotNull() & col("Vietnamese").isNotNull() &
        (trim(col("English")) != "") & (trim(col("Vietnamese")) != "")
    ) \
    .filter(
        ~trim(col("English")).rlike("(?i)^\s*(source|video|\[mp4\]):") &
        ~trim(col("Vietnamese")).rlike("(?i)^\s*word bank:")
    )

    df_final = df \
        .dropDuplicates(["English", "Vietnamese"]) \
        .withColumn("en_len", size(split(trim(col("English")), " "))) \
        .withColumn("vi_len", size(split(trim(col("Vietnamese")), " "))) \
        .filter(
            (col("en_len") >= 3) & (col("vi_len") >= 3) &
            (col("en_len") / col("vi_len") >= 0.5) &
            (col("en_len") / col("vi_len") <= 2.0)
        )   \
        .drop("en_len", "vi_len")

    logger.info("----COMPLETE: BRONZE -> SILVER-----")
    return df_final


def write_to_silver(df: DataFrame, output_path: str):
    """
    Ghi DataFrame đã xử lý xuống Tầng Silver với định dạng Parquet.
    """
    logger.info(f"Writing data to Silver (Parquet) at: {output_path}")

    df.write.mode("overwrite").parquet(output_path)

    logger.info("WRITE COMPLETE")

