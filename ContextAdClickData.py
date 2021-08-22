"""
Feature store manager for Context Ad clicks dataset from kaggle
Link: https://www.kaggle.com/arashnic/ctrtest

#Re-write the featureTable definition as feature store
"""
from copy import Error
import os
from feast import Entity, ValueType, Feature, FeatureView
from feast.data_format import ParquetFormat
from feast import FileSource
from google.protobuf.duration_pb2 import Duration

class ContextAdClickData:

    def __init__(self) -> None:
        self.features = {}

    def train_view_source(self):
        return FileSource(
            event_timestamp_column="impression_time",
                # created_timestamp_column="created",
            file_format=ParquetFormat(),
            path=os.environ.get("TRAIN_DATA"),
        )
    
    def item_data_view_source(self):
        return FileSource(
            file_format=ParquetFormat(),
            path="s3://deploy-mlops-data/data/item_data.parquet"
        )
    
    def view_log_data_view_source(self):
        return FileSource(
            event_timestamp_column="server_time",
            file_format=ParquetFormat(),
            path=os.environ.get("VIEW_LOG_DATA")
        )

    def trainView(self):
        """Defines the train table for the click data.
        :params:
            - column_type_dict - A dictionary of columns and the data type
        
        """
        name = "train_table"
        return FeatureView(
            name=name,
            entities=[self.train_entity().name],
            ttl=Duration(seconds=86400 * 1),
            features=[
                self.feature_create("user_id", ValueType.STRING),
                self.feature_create("impression_id", ValueType.STRING),
                self.feature_create("app_code", ValueType.INT32),
                self.feature_create("os_version", ValueType.STRING),
                self.feature_create("is_4G", ValueType.INT32),
                self.feature_create("is_click", ValueType.INT32),
            ],
            online=True,
            batch_source=self.train_view_source(),
            tags={}
        )
    
    def viewLogView(self):
        name = "view_log_table"
        return FeatureView(
            name=name,
            entities=[self.view_log_entity().name],
            ttl=Duration(seconds=86400 * 1),
            features=[
                # self.feature_create("server_time", ValueType.UNIX_TIMESTAMP),
                self.feature_create("device_type", ValueType.STRING),
                # self.feature_create("session_id", ValueType.INT32),
                self.feature_create("user_id", ValueType.INT64),
                self.feature_create("item_id", ValueType.INT64)
            ],
            online=True,
            batch_source=self.view_log_data_view_source(),
            tags={}
        )

    def itemDataView(self):
        name = "item_data_table"
        feature_table = FeatureView(
            name=name,
            entities=[self.item_data_entity().name],
            ttl=Duration(seconds=86400 * 1),
            features=[
                self.feature_create("item_id", ValueType.INT32),
                self.feature_create("item_price", ValueType.INT32),
                self.feature_create("category_1", ValueType.INT32),
                self.feature_create("category_2", ValueType.INT32),
                self.feature_create("category_3", ValueType.INT32),
                self.feature_create("product_type", ValueType.INT32)
            ],
            online=True,
            batch_source=self.item_data_view_source(),
            tags={}
        )
        return feature_table
        
    
    def train_entity(self):
        name = "impression_id"
        return Entity(name, value_type=ValueType.INT32, description="Impression logs with click details")

    def view_log_entity(self):
        name = "session_id"
        #TODO: Check how to merge the user_id in this entity and user id in click entity.
        return Entity(name=name, value_type=ValueType.INT64, description="View log containing user_id and item_id being viewed")
    
    def item_data_entity(self):
        name="item_id"
        return Entity(name=name, value_type=ValueType.INT32, description="Item data")

    def feature_create(self, name, value):
        """Add features """
        self.features[name] = Feature(name, dtype=value)
        assert name in self.features
        return self.features[name]


addClick = ContextAdClickData()
en_train = addClick.train_entity()
en_view_log = addClick.view_log_entity()
x = addClick.trainView()
# y = addClick.itemDataView()
z = addClick.viewLogView()


# If you have a feature engineering that was done on the dataset in the feature store, 
# You need to provide the feature engineering code while we run it on the version of the parquet folder and 
# Create a new feature on that parquet 