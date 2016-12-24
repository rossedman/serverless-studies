"""EC2 Tag Auditing

This purpose of this script is to provide a working example
of how to audit tags and enforce compliance through serverless
Lambda functions.

This script focuses on enforcing tagging policies. It checks for
required tags on all EC2 instances, checks for appropriate values,
will set tags on first offense and send reminder, then will destroy
instances if they continue to be noncompliant.
"""
from __future__ import print_function
from datetime import datetime, timedelta
import fnmatch
import json
import boto3

client = boto3.client('ec2')

def handler(event, context):

    ### PARAMETERS ###

    # time resources can be non-compliant in days before termination
    noncompliant_threshold = 7

    # required tags, and allowed values
    # allowed values use fnmatch/regex
    required_tags = {
        'environment': [
            'dev',
            'prod',
            'stage'
        ],
        'owner': ['*@gmail.com']
    }

    ### BEGIN AUDIT ###

    # audit resources
    noncompliant_instances = []
    compliant_instances = []
    for instance in get_instance_details(client):
        if not audit_tags(instance['tags'], required_tags):
            noncompliant_instances.append(instance)
        else:
            compliant_instances.append(instance)

    # get records broken down by tasks: terminate, set expiration, terminate in future
    assessed = parse_compliance_status(noncompliant_instances)

    # tag expiration dates
    if assessed['set_expiration']:
        expiration_date = datetime.now() + timedelta(days=noncompliant_threshold)
        client.create_tags(
            Resources=assessed['set_expiration'],
            Tags=[
                {
                    'Key': 'expiration',
                    'Value': expiration_date.strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        )

    # terminate instances that aren't compliant
    if assessed['terminate']:
        client.terminate_instances(
            InstanceIds=assessed['terminate']
        )
        
    print("Compliant: " + json.dumps(compliant_instances))
    print("Noncompliant: " + json.dumps(noncompliant_instances))
    print("Set Expiration Date: " + json.dumps(assessed['set_expiration']))
    print("To Terminate Soon: " + json.dumps(assessed['terminate_soon']))
    print("To Terminate: " + json.dumps(assessed['terminate']))

    #print(noncompliant_instances)
    print("Function Complete")


def get_instance_details(ec2_client):
    """ Get Instance Data

    Retrieve and compile just the data we need from EC2 instances
    """

    # find all instances that are not terminated
    response = ec2_client.describe_instances(
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


def parse_compliance_status(noncompliant_records):
    """Parse Compliance Status

    Assess non compliant record and determine
    whether they need to be terminated, future terminated,
    or expiration date set
    """
    to_terminate = []
    to_set_expiration = []
    to_terminate_soon = []

    for instance in noncompliant_records:
        if 'tags' in instance:
            tag_keys = [t['Key'] for t in instance['tags']]
            if node_first_offense(tag_keys):
                to_set_expiration.append(instance['id'])
            else:
                for tag in instance['tags']:
                    if tag['Key'] == 'expiration':
                        expiration = tag['Value']
                        break

                if node_past_due(expiration):
                    to_terminate.append(instance['id'])
                else:
                    to_terminate_soon.append(instance['id'])
        else:
            to_set_expiration.append(instance['id'])

    return {
        'terminate': to_terminate,
        'terminate_soon': to_terminate_soon,
        'set_expiration': to_set_expiration
    }


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
                return validate_tag_value(tag['Value'], required_tags.get(tag['Key']))
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


def node_first_offense(given_tags):
    """Node First Offense

    If expiration date hasn't been previously set, retrun True
    """
    return 'expiration' not in given_tags


def node_past_due(expiration_date):
    """Node Past Due

    If an expiration date is set on a node, is it past due.
    If it is past due return true

    Timestamp example: 2016-12-22 09:44:41
    """
    return datetime.now() > datetime.strptime(expiration_date, "%Y-%m-%d %H:%M:%S")


