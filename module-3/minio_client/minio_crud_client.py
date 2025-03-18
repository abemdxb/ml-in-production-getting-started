"""
MinIO CRUD Client

This module provides a client for performing CRUD operations on a MinIO server.
It supports creating, reading, updating, and deleting objects and buckets.
"""

import io
import os
import json
from typing import Dict, List, Optional, Union, BinaryIO, Tuple, Iterator
import logging
from urllib3.exceptions import MaxRetryError

from minio import Minio
from minio.error import S3Error
from minio.commonconfig import Tags

from .config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MinioCrudClient:
    """
    A client for performing CRUD operations on a MinIO server.
    
    This client provides methods for creating, reading, updating, and deleting
    objects and buckets in a MinIO server.
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        secure: Optional[bool] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize the MinIO CRUD client.
        
        Args:
            endpoint: MinIO server endpoint (host:port)
            access_key: MinIO access key
            secret_key: MinIO secret key
            secure: Whether to use HTTPS
            region: MinIO region
        """
        config = get_config(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            region=region,
        )
        
        self.client = Minio(
            endpoint=config["endpoint"],
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            secure=config["secure"],
            region=config["region"],
        )
        
        logger.info(f"Initialized MinIO client for endpoint: {config['endpoint']}")

    # ===== Bucket Operations =====
    
    def create_bucket(self, bucket_name: str, location: str = "us-east-1") -> bool:
        """
        Create a new bucket.
        
        Args:
            bucket_name: Name of the bucket to create
            location: Region where the bucket will be created
            
        Returns:
            bool: True if bucket was created, False if it already exists
            
        Raises:
            S3Error: If there was an error creating the bucket
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name, location=location)
                logger.info(f"Created bucket: {bucket_name}")
                return True
            else:
                logger.info(f"Bucket already exists: {bucket_name}")
                return False
        except S3Error as e:
            logger.error(f"Error creating bucket {bucket_name}: {e}")
            raise

    def list_buckets(self) -> List[Dict[str, str]]:
        """
        List all buckets.
        
        Returns:
            List of dictionaries containing bucket information
            
        Raises:
            S3Error: If there was an error listing buckets
        """
        try:
            buckets = self.client.list_buckets()
            return [
                {"name": bucket.name, "creation_date": bucket.creation_date.isoformat()}
                for bucket in buckets
            ]
        except S3Error as e:
            logger.error(f"Error listing buckets: {e}")
            raise

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if a bucket exists.
        
        Args:
            bucket_name: Name of the bucket to check
            
        Returns:
            bool: True if bucket exists, False otherwise
            
        Raises:
            S3Error: If there was an error checking bucket existence
        """
        try:
            return self.client.bucket_exists(bucket_name)
        except S3Error as e:
            logger.error(f"Error checking if bucket {bucket_name} exists: {e}")
            raise

    def remove_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Remove a bucket.
        
        Args:
            bucket_name: Name of the bucket to remove
            force: If True, remove all objects in the bucket before removing the bucket
            
        Returns:
            bool: True if bucket was removed, False if it doesn't exist
            
        Raises:
            S3Error: If there was an error removing the bucket
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                logger.info(f"Bucket does not exist: {bucket_name}")
                return False
                
            if force:
                # Remove all objects in the bucket first
                objects = self.client.list_objects(bucket_name, recursive=True)
                objects_to_delete = [obj.object_name for obj in objects]
                
                if objects_to_delete:
                    errors = self.client.remove_objects(bucket_name, objects_to_delete)
                    for error in errors:
                        logger.error(f"Error removing object: {error}")
            
            self.client.remove_bucket(bucket_name)
            logger.info(f"Removed bucket: {bucket_name}")
            return True
        except S3Error as e:
            logger.error(f"Error removing bucket {bucket_name}: {e}")
            raise

    # ===== Object Operations =====
    
    def upload_object(
        self,
        bucket_name: str,
        object_name: str,
        data: Union[str, bytes, BinaryIO],
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        part_size: int = 10 * 1024 * 1024,  # 10MB
    ) -> Dict[str, str]:
        """
        Upload an object to a bucket.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object
            data: Data to upload (string, bytes, or file-like object)
            content_type: Content type of the object
            metadata: Metadata to attach to the object
            tags: Tags to attach to the object
            part_size: Part size for multipart uploads
            
        Returns:
            Dictionary containing etag and version_id
            
        Raises:
            S3Error: If there was an error uploading the object
        """
        try:
            # Create bucket if it doesn't exist
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data = data.encode("utf-8")
                if content_type is None:
                    content_type = "text/plain"
            
            # Convert bytes to BytesIO if necessary
            if isinstance(data, bytes):
                data_size = len(data)
                data = io.BytesIO(data)
            else:
                # Get file size for file-like objects
                data.seek(0, os.SEEK_END)
                data_size = data.tell()
                data.seek(0)
                
                if content_type is None:
                    content_type = "application/octet-stream"
            
            # Prepare tags if provided
            tag_obj = None
            if tags:
                tag_obj = Tags(for_object=True)
                for key, value in tags.items():
                    tag_obj[key] = value
            
            # Upload the object
            result = self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=data_size,
                content_type=content_type,
                metadata=metadata,
                tags=tag_obj,
                part_size=part_size,
            )
            
            logger.info(f"Uploaded object: {bucket_name}/{object_name}")
            return {
                "etag": result.etag,
                "version_id": result.version_id,
            }
        except S3Error as e:
            logger.error(f"Error uploading object {bucket_name}/{object_name}: {e}")
            raise

    def download_object(
        self, bucket_name: str, object_name: str, version_id: Optional[str] = None
    ) -> Tuple[bytes, Dict[str, str]]:
        """
        Download an object from a bucket.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object
            version_id: Version ID of the object
            
        Returns:
            Tuple containing the object data and metadata
            
        Raises:
            S3Error: If there was an error downloading the object
        """
        try:
            response = self.client.get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                version_id=version_id,
            )
            
            # Read the data
            data = response.read()
            
            # Get the metadata
            metadata = {
                "content_type": response.headers.get("Content-Type", ""),
                "etag": response.headers.get("ETag", "").strip('"'),
                "last_modified": response.headers.get("Last-Modified", ""),
                "size": response.headers.get("Content-Length", ""),
            }
            
            # Add custom metadata
            for key, value in response.headers.items():
                if key.lower().startswith("x-amz-meta-"):
                    metadata_key = key[len("x-amz-meta-"):].lower()
                    metadata[metadata_key] = value
            
            response.close()
            response.release_conn()
            
            logger.info(f"Downloaded object: {bucket_name}/{object_name}")
            return data, metadata
        except S3Error as e:
            logger.error(f"Error downloading object {bucket_name}/{object_name}: {e}")
            raise

    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        recursive: bool = False,
    ) -> List[Dict[str, str]]:
        """
        List objects in a bucket.
        
        Args:
            bucket_name: Name of the bucket
            prefix: Prefix to filter objects
            recursive: Whether to list objects recursively
            
        Returns:
            List of dictionaries containing object information
            
        Raises:
            S3Error: If there was an error listing objects
        """
        try:
            objects = self.client.list_objects(
                bucket_name=bucket_name,
                prefix=prefix,
                recursive=recursive,
            )
            
            return [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "etag": obj.etag.strip('"') if obj.etag else None,
                }
                for obj in objects
            ]
        except S3Error as e:
            logger.error(f"Error listing objects in bucket {bucket_name}: {e}")
            raise

    def object_exists(
        self, bucket_name: str, object_name: str
    ) -> bool:
        """
        Check if an object exists in a bucket.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object
            
        Returns:
            bool: True if object exists, False otherwise
            
        Raises:
            S3Error: If there was an error checking object existence
        """
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            logger.error(f"Error checking if object {bucket_name}/{object_name} exists: {e}")
            raise

    def get_object_metadata(
        self, bucket_name: str, object_name: str, version_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get metadata for an object.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object
            version_id: Version ID of the object
            
        Returns:
            Dictionary containing object metadata
            
        Raises:
            S3Error: If there was an error getting object metadata
        """
        try:
            stat = self.client.stat_object(
                bucket_name=bucket_name,
                object_name=object_name,
                version_id=version_id,
            )
            
            metadata = {
                "size": stat.size,
                "etag": stat.etag.strip('"') if stat.etag else None,
                "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
                "content_type": stat.content_type,
                "version_id": stat.version_id,
            }
            
            # Add custom metadata
            if stat.metadata:
                for key, value in stat.metadata.items():
                    if key.lower().startswith("x-amz-meta-"):
                        metadata_key = key[len("x-amz-meta-"):].lower()
                        metadata[metadata_key] = value
            
            return metadata
        except S3Error as e:
            logger.error(f"Error getting metadata for object {bucket_name}/{object_name}: {e}")
            raise

    def update_object(
        self,
        bucket_name: str,
        object_name: str,
        data: Union[str, bytes, BinaryIO],
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Update an object in a bucket.
        
        This is essentially the same as uploading a new object with the same name,
        which will overwrite the existing object.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object
            data: Data to upload (string, bytes, or file-like object)
            content_type: Content type of the object
            metadata: Metadata to attach to the object
            tags: Tags to attach to the object
            
        Returns:
            Dictionary containing etag and version_id
            
        Raises:
            S3Error: If there was an error updating the object
        """
        return self.upload_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            content_type=content_type,
            metadata=metadata,
            tags=tags,
        )

    def copy_object(
        self,
        source_bucket: str,
        source_object: str,
        dest_bucket: str,
        dest_object: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Copy an object from one location to another.
        
        Args:
            source_bucket: Source bucket name
            source_object: Source object name
            dest_bucket: Destination bucket name
            dest_object: Destination object name (if None, use source_object)
            metadata: New metadata to apply to the destination object
            
        Returns:
            Dictionary containing etag and version_id
            
        Raises:
            S3Error: If there was an error copying the object
        """
        try:
            if dest_object is None:
                dest_object = source_object
                
            # Create destination bucket if it doesn't exist
            if not self.client.bucket_exists(dest_bucket):
                self.client.make_bucket(dest_bucket)
                logger.info(f"Created bucket: {dest_bucket}")
            
            result = self.client.copy_object(
                bucket_name=dest_bucket,
                object_name=dest_object,
                source_bucket_name=source_bucket,
                source_object_name=source_object,
                metadata=metadata,
            )
            
            logger.info(f"Copied object from {source_bucket}/{source_object} to {dest_bucket}/{dest_object}")
            return {
                "etag": result.etag,
                "version_id": result.version_id,
            }
        except S3Error as e:
            logger.error(f"Error copying object from {source_bucket}/{source_object} to {dest_bucket}/{dest_object}: {e}")
            raise

    def remove_object(
        self, bucket_name: str, object_name: str, version_id: Optional[str] = None
    ) -> bool:
        """
        Remove an object from a bucket.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object
            version_id: Version ID of the object
            
        Returns:
            bool: True if object was removed, False if it doesn't exist
            
        Raises:
            S3Error: If there was an error removing the object
        """
        try:
            # Check if object exists
            try:
                self.client.stat_object(bucket_name, object_name, version_id=version_id)
            except S3Error as e:
                if e.code == "NoSuchKey":
                    logger.info(f"Object does not exist: {bucket_name}/{object_name}")
                    return False
                raise
                
            self.client.remove_object(
                bucket_name=bucket_name,
                object_name=object_name,
                version_id=version_id,
            )
            
            logger.info(f"Removed object: {bucket_name}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error removing object {bucket_name}/{object_name}: {e}")
            raise

    def remove_objects(
        self, bucket_name: str, object_names: List[str]
    ) -> List[Dict[str, str]]:
        """
        Remove multiple objects from a bucket.
        
        Args:
            bucket_name: Name of the bucket
            object_names: List of object names to remove
            
        Returns:
            List of dictionaries containing error information for failed deletions
            
        Raises:
            S3Error: If there was an error removing objects
        """
        try:
            errors = list(self.client.remove_objects(bucket_name, object_names))
            
            if not errors:
                logger.info(f"Removed {len(object_names)} objects from bucket {bucket_name}")
            else:
                logger.warning(f"Removed objects with {len(errors)} errors from bucket {bucket_name}")
                
            return [
                {
                    "object_name": error.object_name,
                    "error_code": error.error_code,
                    "error_message": error.error_message,
                }
                for error in errors
            ]
        except S3Error as e:
            logger.error(f"Error removing objects from bucket {bucket_name}: {e}")
            raise

    # ===== Utility Methods =====
    
    def get_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires: int = 3600,
        response_headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Get a presigned URL for an object.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object
            expires: Expiration time in seconds
            response_headers: Response headers to override
            
        Returns:
            Presigned URL
            
        Raises:
            S3Error: If there was an error generating the presigned URL
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=expires,
                response_headers=response_headers,
            )
            
            logger.info(f"Generated presigned URL for {bucket_name}/{object_name}")
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL for {bucket_name}/{object_name}: {e}")
            raise

    def is_connected(self) -> bool:
        """
        Check if the client is connected to the MinIO server.
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            # Try to list buckets as a simple connectivity test
            self.client.list_buckets()
            return True
        except (S3Error, MaxRetryError) as e:
            logger.error(f"Error connecting to MinIO server: {e}")
            return False
