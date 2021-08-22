Feature ups for a recommendation system

The idea here is to create a pipeline feature store with feast that is deployed on a kubernetes cluster. All Dataops approaches will be created as new docker container and deployed on kubernetes using Argo CD


The aim of this application is:
To singly update our feature store both online and offline and also materiaalize the online store for any new update

#TODO:
- Write unittest to ensure that new data are optimally being validated against recent feature stores
- Things are not going to break on new data addition
- Incorporate monitoring dashboard for the feature store.

Where to keep the online store?


#TODO:
Fix feature-store deployment - We need a better way to run the feast apply from the command - since it stops on run. maybe what we even need is to do feast materialize instead 
