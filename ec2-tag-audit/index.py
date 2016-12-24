from __future__ import print_function
import boto3
import fnmatch

client = boto3.client('ec2')

def handler(event, context):

    # tags that all resources will be checked against
    required_tags = {
        'environment': [
            'dev',
            'prod',
            'stage'
        ],
        'owner': ['*@gmail.com']
    }

    # audit resources
    terminate = []
    for instance in get_instance_details():
        if not audit_tags(instance['tags'], required_tags):
            terminate.append(instance['id'])

    # terminate nodes that are not compliant
    client.terminate_instances(
        InstanceIds=terminate
    )

    print(terminate)
    print("Function Complete")


def get_instance_details():
    """ Get Instance Data

    Retrieve and compile just the data we need from EC2 instances
    """

    # find all instances that are not terminated
    response = client.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                    'shutting-down',
                    'stopped',
                    'stopping',
                    'pending'
                ]
            }
        ]
    )

    # aggregate results into easy format to work with
    results = []
    for instance in response['Reservations'][0]['Instances']:
        results.append({
            'id': instance.get('InstanceId'),
            'tags': instance.get('Tags', {})
        })

    return results


def audit_tags(given_tags, required_tags):
    """Audit All Tags

    Assesses the tags in as much detail as possible to reach a conclusion 
    about the current resource. 
    """
    # validate the keys of tags first
    if validate_tag_keys([t['Key'] for t in given_tags], required_tags.keys()):
        # validate values of each tag
        for tag in given_tags:
            # if tag exist in required_tags, lets check values
            if required_tags.get(tag['Key']):
                if not validate_tag_value(tag['Value'], required_tags.get(tag['Key'])):
                    return False
        return True
    else:
        return False


def validate_tag_value(given_value, accepted_values):
    """Audit Tag Values

    Will assess the value passed in and determine if it meets the
    requirements that are contained in the `required_tags` array at
    the top of the script

    given_value: string
        The value of the tag we are auditing

    accepted_values: list
        All of the accepted values that are accepted, wildcards included
    """
    for value in accepted_values:
        if fnmatch.fnmatch(given_value, value):
            return True

    return False


def validate_tag_keys(given_tag_keys, required_tag_keys):
    """Validate Set Tags

    Audits the keys provided by the resource and compares them to 
    the required tags. 

    given_tag_keys: list 

    required_tag_keys: list
    """
    return required_tag_keys == list(set(given_tag_keys).intersection(required_tag_keys))
