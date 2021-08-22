import boto3
from botocore.client import Config
import os
from pathlib import Path
from textwrap import dedent
import logging

# TODO: Before you migrate a new feast feature, we should first download existing feast store from aws/minio if
# it exists else we go ahead an creat it so that we update exising feast repo first

class DataRetrieveError(Exception):
    
    def __init__(self, *args: object) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        if self.message:
            return f'DataRetrieveError, {self.message}'
        else:
            return 'DataRetrieveError:'


def connect_to_s3():
    """Should connect """
    s3 = boto3.resource('s3',
    # Should probably check to ensure that the various env variables are given.
        endpoint_url = os.environ.get('MINIO_SERVER_ENDPOINT'),
        aws_access_key_id=os.environ.get('ACESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('SECRET_ACCESSKEY'),
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

    return s3

def retrieve_feature_db(s3_client, bucket_name, file_name, download_location):
    """Should retrieve feature db to a local file directory in the container"""
    try:
        os.makedirs(download_location, exist_ok=True)
    except FileExistsError as err:
        logging.info("File already existed hence parsing")
        pass
    return s3_client.Bucket(bucket_name).download_file(file_name, os.path.join(download_location, file_name))

def push_feature_db(s3_client, bucket_name, file_name, upload_location):
    """Should upload feature db back to minio s3 server
    This should happen when we intend to push a zipped offline or online db back to minio.
    """
    return s3_client.meta.client.upload_file(file_name, bucket_name, os.path.basename(file_name))

def write_feature_yaml( project_name, data_path):
    path = Path('.')
    feature_yaml_path = path / 'feature_store.yaml'

    # Write the feature yaml config to the root folder of the project
    feature_yaml_path.write_text(
            dedent(
                f"""
            project: {project_name}
            registry: {str(Path(data_path) / 'registry.db')}
            provider: local
            online_store:
                path: {str(Path(data_path) / 'online_store.db')}
                """
            )
        )
    return feature_yaml_path

def zip_file( zip_file_name, file_db_path):
    from zipfile import ZipFile
    try:
        # Zip the file
        zp = ZipFile(zip_file_name, mode='w')
        zp.write(file_db_path)
        zp.close()
        is_created = os.path.exists(zip_file_name)
        if not is_created:
            print("Couldn't create zip file")
            raise FileNotFoundError("Couldn't create the zip file") 
        return zip_file_name
    except Exception as ex:
        # Unable to zip
        print(str(ex))
        return False

def run_feast_apply_cmd():
    """Run the feast apply command from the python shell"""
    import subprocess
    call = subprocess.run(["feast", "apply"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("Running call")
    print(call.stdout.decode('utf-8'))
    return call.returncode == 0

def retrieve_data_s3(s3_client, bucket_name, data, download_path):
    try:
        retrieve_feature_db(s3_client, bucket_name, data, download_path)
    except Exception as ex:
        logging.error(f"Couldn't retrieve data {data} with {str(ex)}")
        raise DataRetrieveError(f"Error retrieving {data} data from s3 with {str(ex)}")

def feast_run(file_path = "/tmp/data"):
    s3 = connect_to_s3()
    data_bucket_name = "deploy-mlops-data"
    # Download the data from s3.
    # TRAIN_DATA
    train_data = "train.parquet"
    retrieve_data_s3(s3, data_bucket_name, train_data, file_path)
    os.environ['TRAIN_DATA'] = os.path.join(file_path, train_data)
    # VIEW_DATA
    view_data = "view_log.parquet"
    retrieve_data_s3(s3, data_bucket_name, view_data, file_path)
    os.environ['VIEW_LOG_DATA'] = os.path.join(file_path, view_data)

    # Generate the yaml.
    write_feature_yaml('click_ad_feast', file_path)
    assert os.path.exists('./feature_store.yaml') == True, "Error creating feature store yaml."
    # Migrate the data to the specified path.
    response = run_feast_apply_cmd()
    assert response == True, "Feast apply command failed"
    # Generate zip for offline
    offline_data_path = Path(file_path) / 'registry.db'
    # offline_zip = zip_file('offline.zip', offline_data_path)
    # Generate zip for online
    online_data_path = Path(file_path) / 'online_store.db'
    # online_zip = zip_file('online_store.zip', online_data_path)
    
    # Push the zipped data to minio.
    
    upload_bucket = 'deploy-mlops'
    upload_location = 'feast/'
    push_feature_db(s3, upload_bucket, str(offline_data_path), upload_location)
    push_feature_db(s3, upload_bucket, str(online_data_path), upload_location)

    # Cleanups
    import shutil
    shutil.rmtree(file_path, ignore_errors=True)
    # os.remove(online_zip)
    # os.remove(offline_zip)
    os.remove('./feature_store.yaml')


# Entry point of the application for feast
if __name__ == "__main__":
    feast_run() 