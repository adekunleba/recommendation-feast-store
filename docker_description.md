### Feature Ops with feast

#### Project Description
The docker image is the deployment for feature ops using feast. 

The project makes use of s3 as the file source. We deployed minio on kubernetes running locally and can use that instance as our datasource for the project

There are couple of environment variables that is needed to be set to ensure that the project works well

```
<!-- Project specific environment -->
VIEW_LOG_DATA
TRAIN_DATA


<!-- container environment -->
FEAST_S3_ENDPOINT_URL
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```