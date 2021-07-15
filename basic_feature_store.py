"""
Basic feature store class.
Feature store is the basis for feature engineering. It is a deployment pipeline on it's own 
When creating a CI/CD for this, you will need to engineer deployment of a feature store yaml or something
after rigorous testing.

E.g given a new data source, how do you store it to the feature store and how do you join it with existing data
for re-engineered dataset

The Goal of a feature store is to have a consolidated source of truth for all organizational features
"""

class FeatureStore:

    def __init__(self, source) -> None:
        pass

    def initialize(self, core_url:str, serving_url:str):
        """Connect to the feature store client"""