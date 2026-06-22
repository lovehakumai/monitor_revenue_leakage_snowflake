from snowflake.snowpark.context import get_active_session
import pandas as pd
import polars as pl
import io
from zipfile import ZipFile

# =============================================-
# MAIN PROCESS
# =============================================-
def create_table_from_zip(session, zip_full_path, target_db, target_schema):
    file_stream = session.file.get_stream(zip_path, decompress=False) # decompress is used when the file is single compressed files like .gzip
    file_cnt = 1
    with ZipFile(file_stream) as zip:
        all_name_list = zip.namelist()
        target_name_list = [v for v in all_name_list if v.endswith('.csv')]
        for nm in target_name_list:
        
            print('='*100)
            print(f'PROCESS START FILE NO {file_cnt} OUT OF {len(target_name_list)}')
            file_name = nm.replace('.csv', '').upper()

            print(f'Making Parquet file {file_name}.parquet')
            bytes_io = io.BytesIO() 
            buffer = zip.read(nm)
            pl_df = pl.read_csv(io.BytesIO(buffer))
            pl_df.columns = [col.upper() for col in pl_df.columns]
            pl_df.write_parquet(bytes_io)
            bytes_io.seek(0)
            
            source_db_name = zip_full_path.split('.')[0].replace('@', '')
            source_schema_name = zip_full_path.split('.')[1]
            source_stg_name = zip_full_path.split('.')[2].split('/')[0]
            session.sql(f"USE DATABASE {source_db_name}")
            
            session.file.put_stream(
                input_stream = bytes_io,
                stage_location = f'@{source_db_name}.{source_schema_name}.{source_stg_name}/{file_name}.parquet',
                auto_compress = False,
                overwrite = True
            )
            print('Finished!!!')
            
            table_name = f"{target_db}.{target_schema}.RAW_{file_name}"
            print(f'Creating Table {table_name}')

            session.read.parquet(
                path = f'@{source_db_name}.{source_schema_name}.{source_stg_name}/{file_name}.parquet'
                ).write.save_as_table(
                    table_name = table_name ,
                    mode = "overwrite"
                )
            
            print('Finished!!!')
            
            if file_cnt < len(target_name_list):
                file_cnt += 1
    print(f"Finished Create {file_cnt} Tables, ")

session = get_active_session()
zip_path = '@KAGGLE_SUBSCRIPTION.PUBLIC.COMPRESSED_DATASETS/SaaS_Subsciption_Churn_Analytics_Dataset.zip'

create_table_from_zip(session, zip_full_path=zip_path, target_db='KAGGLE_SUBSCRIPTION', target_schema='RAW')