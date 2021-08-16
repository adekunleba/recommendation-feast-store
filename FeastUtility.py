import boto3
from botocore.client import Config
import os
from pathlib import Path
from textwrap import dedent

# TODO: Before you migrate a new feast feature, we should first download existing feast store from aws/minio if
# it exists else we go ahead an creat it so that we update exising feast repo first

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

    return s3_client.Bucket(bucket_name).download_file(file_name, download_location)

def push_feature_db(s3_client, bucket_name, file_name, upload_location):
    """Should upload feature db back to minio s3 server
    This should happen when we intend to push a zipped offline or online db back to minio.
    """
    return s3_client.Bucket(bucket_name).upload_file(upload_location, file_name)

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
    print(call.stdout.decode('utf-8'))
    return call.returncode == 0


def feast_run(file_path = "/tmp/data"):
    # Generate the yaml.
    write_feature_yaml('click_ad_feast', file_path)
    assert os.path.exists('./feature_store.yaml') == True, "Error creating feature store yaml."
    # Migrate the data to the specified path.
    response = run_feast_apply_cmd()
    assert response == True, "Feast apply command failed"
    # Generate zip for offline
    offline_data_path = Path(file_path) / 'registry.db'
    offline_zip = zip_file('offline.zip', offline_data_path)
    # Generate zip for online
    online_data_path = Path(file_path) / 'online_store.db'
    online_zip = zip_file('online_store.zip', online_data_path)
    
    # Push the zipped data to minio.
    s3 = connect_to_s3()
    upload_bucket = 'deploy_mlops'
    upload_location = 'feast/'
    push_feature_db(s3, upload_bucket, offline_zip, upload_location)
    push_feature_db(s3, upload_bucket, online_zip, upload_location)

# Entry point of the application for feast
if __name__ == "__main__":
    feast_run() 