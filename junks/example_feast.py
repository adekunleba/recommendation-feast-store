from datetime import datetime
import pandas as pd

from feast import FeatureStore

entity_df = pd.DataFrame.from_dict({
    "driver_id": [1001, 1002, 1003, 1004],
        "event_timestamp": [
            datetime(2021, 4, 12, 10, 59, 42),
            datetime(2021, 4, 12, 8, 12, 10),
            datetime(2021, 4, 12, 16, 40, 26),
            datetime(2021, 4, 12, 15, 1, 12),
        ],
})

print(entity_df.head(5))


#Load/Connect to store
store = FeatureStore(repo_path="feature_repo")

training_df = store.get_historical_features(entity_df=entity_df, feature_refs=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
    ],
).to_df()

print("-----Extracted df \n", training_df.head())

from pprint import pprint

feature_vector = store.get_online_features(
    feature_refs=[
        "driver_hourly_stats:conv_rate", #FeatureView:ColumnName
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
    ],
    entity_rows=[{"driver_id": 1001}],
).to_dict()

pprint(feature_vector)

try_read_parquet = pd.read_parquet("./feature_repo/data/driver_stats.parquet")
print("Parquet data \n", try_read_parquet.head(10))