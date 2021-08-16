# """
# Basic feature store class.
# Feature store is the basis for feature engineering. It is a deployment pipeline on it's own 
# When creating a CI/CD for this, you will need to engineer deployment of a feature store yaml or something
# after rigorous testing.

# E.g given a new data source, how do you store it to the feature store and how do you join it with existing data
# for re-engineered dataset

# The Goal of a feature store is to have a consolidated source of truth for all organizational features
# """

# import boto3
# from botocore.client import Config
# import pandas as pd
# from datetime import datetime
# from feast import FeatureStore

# import json
# json.dum

# store = FeatureStore(repo_path=".")

# entity_df = pd.DataFrame.from_dict({
#     "session_id": [218564],
#     "event_timestamp" : datetime(2018, 10, 15, 8, 58, 00),
# })

# data_df = store.get_historical_features(feature_refs=["view_log_table:device_type"], entity_df=entity_df)
# ex_data = data_df.to_df()


# # s3 = boto3.resource('s3',
# #                     endpoint_url='http://localhost:8081/',
# #                     aws_access_key_id='minio',
# #                     aws_secret_access_key='minio123',
# #                     config=Config(signature_version='s3v4'),
# #                     region_name='us-east-1')

# if __name__ == "__main__":
#     # s3.Bucket('deploy-mlops-data').upload_file('/Users/adekunleba/MyProjects/mlops/feature_ops/data/train.parquet','train.parquet')
#     # s3.Bucket('deploy-mlops-data').upload_file('/Users/adekunleba/MyProjects/mlops/feature_ops/data/view_log.parquet','view_log.parquet')
#     print(ex_data.head())
