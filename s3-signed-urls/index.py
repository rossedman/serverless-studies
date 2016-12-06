"""S3 Object Storage/Presigned URLs

This is a simple application that stores object metadata and generates
presigned URLs for external third-party access to downloads. Also includes
a lambda to clean up after itself when objects are deleted.

The purpose of this is to show a simple application being built with lambda
functions.
"""
import os
import boto3

def store(event, context):
    """Object Storage Function

    This will record any new or altered s3 objects in the
    DynamoDB instance and generate presigned URLs for some
    kind of third party distribution
    """

    buckets = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    try:
        for record in event['Records']:

            # retrieve filename of record
            keyname = record['s3']['object']['key']

            # skip if is directory
            if keyname.endswith("/"):
                continue

            # generate presigned url
            url = buckets.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': record['s3']['bucket']['name'],
                    'Key': keyname
                }
            )

            # store in dynamodb
            table.put_item(
                Item={
                    'id': keyname,
                    'time': record['eventTime'],
                    'ip': record['requestParameters']['sourceIPAddress'],
                    'size': record['s3']['object']['size'],
                    'url': url
                }
            )

    except Exception as e:
        print 'Function failed due to exception.'
        print e

    print 'Function complete.'
    return 'Function complete.'



def remove(event, context):
    """Object Removal Function

    Whenever an object is removed from storage it will also be
    removed from the DynamoDB instance.

    This could be used to trigger some other kind of audit event
    at some point.
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    try:
        for record in event['Records']:

            # retrieve filename of record
            keyname = record['s3']['object']['key']

            # skip if is directory
            if keyname.endswith("/"):
                continue

            # delete record from table
            table.delete_item(
                Key={
                    'id': keyname
                }
            )

    except Exception as e:
        print 'Function failed due to exception.'
        print e

    print 'Function complete.'
    return 'Function complete.'
