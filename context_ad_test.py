from subprocess import run
import unittest
from FeastUtility import write_feature_yaml, run_feast_apply_cmd, zip_file, retrieve_feature_db, connect_to_s3
import os
from pathlib import Path
class ContextAdClickDataTest(unittest.TestCase):

    def test_example(self):
        self.assertEqual(True, True)

    def test_create_yaml(self):
        # Write to filepath
        repo_path = Path('./test')
        write_feature_yaml('test_example', str(repo_path))
        self.assertTrue(os.path.exists('./feature_store.yaml'))
        os.remove("./feature_store.yaml")
        self.assertFalse(os.path.exists("./feature_store.yaml"))

    
    def test_run_apply(self):
        repo_path = Path('./test')
        write_feature_yaml('test_example', str(repo_path))
        os.environ["TRAIN_DATA"] =  "test/train.parquet"
        os.environ["VIEW_LOG_DATA"] = "test/view_log.parquet"

        

        status = run_feast_apply_cmd()
        self.assertTrue(status)
        self.assertTrue(os.path.exists(repo_path / 'registry.db'))
        self.assertTrue(os.path.exists(repo_path / 'online_store.db'))

        # os.remove(repo_path / 'registry.db')
        os.remove(repo_path / 'online_store.db')
        os.remove("./feature_store.yaml")
        self.assertFalse(os.path.exists(repo_path / 'online_store.db'))


    def test_check_create_zip(self):
        zip_file_name = "./test/registry.zip"
        ret = zip_file(zip_file_name, "./test/registry.db")
        self.assertEqual(zip_file_name, ret)
        self.assertTrue(os.path.exists("./test/registry.zip"))
        os.remove("./test/registry.zip")
        self.assertFalse(os.path.exists("./test/registry.zip"))

    
    def test_retrieve_data_s3(self):
        os.environ["MINIO_SERVER_ENDPOINT"] =  "http://localhost:8000"
        os.environ["ACESS_KEY_ID"] = "minio"
        os.environ["SECRET_ACCESSKEY"]  = "minio123"

        download_path = "/tmp/data"
        data = "train.parquet"
        s3_client = connect_to_s3()
        retrieve_feature_db(
            s3_client=s3_client,
            bucket_name="deploy-mlops-data",
            file_name=data,
            download_location=download_path
        )
        self.assertTrue(os.path.exists(os.path.join(download_path, data)))
        os.remove(os.path.join(download_path, data))
        os.rmdir(download_path)
        



if __name__ == "__main__":
    unittest.main()