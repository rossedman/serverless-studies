"""EC2 Tag Audit & Terminate

This lambda will analyze all EC2 resource tags and whatever instances
do not meet the required_tags array will be terminated.

Notice that in the index.yaml file there is a cron expression. Currently
this is set to run every Friday at 6PM.
"""
import boto3

def handler(event, context):
    """Tag Audit

    Audit tags that are present on running EC2 instances, if they are not
    terminate the instances.
    """
    to_terminate = []

    required_tags = [
        "environment",
        "owner"
    ]

    client = boto3.client('ec2')

    reservations = client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    ).get('Reservations', [])

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], []
    )

    for ins in instances:
        if 'Tags' in ins:
            keys = [d['Key'] for d in ins['Tags']]
            if keys != required_tags:
                to_terminate.append(ins['InstanceId'])
        else:
            to_terminate.append(ins['InstanceId'])

    if to_terminate:
        client.stop_instances(InstanceIds=to_terminate)

        return {
            "terminated": to_terminate
        }
