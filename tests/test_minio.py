#test_minio.py
import unittest
from unittest.mock import patch, MagicMock, mock_open
from minio import Minio
from minio.error import S3Error
import os
import logging
from app.utils.minio import getClient, createBucket, uploadImage

@patch('os.getenv')
@patch('minio.Minio')
def test_getClient(mock_minio, mock_getenv):
    """Test Create and Return Client instance"""
    mock_getenv.side_effect = lambda key: {
        "MINIO_URL": "localhost:9000",
        "MINIO_ACCESS_KEY": "access_key",
        "MINIO_SECRET_KEY": "secret_key"
    }[key]

    client = getClient()
    assert isinstance(client, Minio)


def test_createBucket():
    """Test bucket creation"""
    mock_client = MagicMock()
    mock_client.bucket_exists.return_value = False

    createBucket(mock_client)

    mock_client.bucket_exists.assert_called_once_with("profiles")
    mock_client.make_bucket.assert_called_once_with("profiles")
    logging.info("Bucket 'profiles' created.")

def test_createBucketAlreadyExists():
    """Test attempt create bucket when already exists"""
    mock_client = MagicMock()
    mock_client.bucket_exists.return_value = True
    
    createBucket(mock_client)
    
    mock_client.bucket_exists.assert_called_with("profiles")
    assert mock_client.make_bucket.call_count == 0

@patch('minio.Minio.fput_object')
@patch('minio.Minio.bucket_exists')
@patch('minio.Minio.make_bucket')
def test_uploadImage(mock_make_bucket, mock_bucket_exists, mock_fput_object):
    """Test upload image"""
    mock_client = MagicMock()
    mock_client.bucket_exists.return_value = False
    
    uploadImage(mock_client, 'test_path/image.jpg', 'image.jpg')
    
    mock_client.bucket_exists.assert_called_once_with("profiles")
    mock_client.make_bucket.assert_called_once_with("profiles")
    mock_client.fput_object.assert_called_once_with("profiles", "image.jpg", 'test_path/image.jpg')

@patch('minio.Minio.fput_object')
@patch('app.utils.minio.createBucket')
def test_uploadImageError(mock_createBucket, mock_fput_object):
    """Test for upload image error with fake path or fake image"""
    mock_client = MagicMock()

    mock_client.fput_object.side_effect = S3Error(
        code="MinIO error",
        message="error message",
        resource="resource",
        request_id="request_id",
        host_id="host_id",
        response=MagicMock()
    )

    with patch("builtins.open", mock_open(read_data="data")):
        with unittest.TestCase().assertLogs(level='ERROR') as log:
            uploadImage(mock_client, "fake_path", "fake_image")

            assert any("Error uploading image" in message for message in log.output)

