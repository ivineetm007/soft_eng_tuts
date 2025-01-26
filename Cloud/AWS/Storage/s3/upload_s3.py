import boto3


def upload_to_s3(file_path, bucket_name, object_name, aws_access_key_id, aws_secret_access_key):
    """
    Uploads a file to an S3 bucket using the provided AWS credentials.

    Parameters:
        file_path (str): Path to the file you want to upload.
        bucket_name (str): The name of the S3 bucket.
        object_name (str): The desired name of the file within the bucket.
        aws_access_key_id (str): Your AWS access key id.
        aws_secret_access_key (str): Your AWS secret key.
    """
    # Create an S3 client using the provided credentials
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    try:
        # Upload the file to the S3 bucket
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"{file_path} successfully uploaded to {bucket_name}/{object_name}.")
    except Exception as e:
        print(f"Error uploading {file_path} to {bucket_name}/{object_name}: {e}")


# Example usage:
file_path = './sample.txt'
bucket_name = 'bucket'
object_name = 'smaple1/file.txt'
aws_access_key_id = '<ACCESS_ID>'
aws_secret_access_key = '<ACCESS_KEY>'

upload_to_s3(file_path, bucket_name, object_name, aws_access_key_id, aws_secret_access_key)
