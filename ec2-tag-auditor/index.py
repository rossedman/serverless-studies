
import boto3


def handler(event, context):
    """Tag Audit

    Audit tags that are present on running EC2 instances
    """
    required_tags = ["Something", "Crazy"]
    to_terminate = []
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

    print instances

    for ins in instances:
        # TODO: check if Tags are set, if not terminate
        if 'Tags' in ins:
            keys = [d['Key'] for d in ins['Tags']]
            if keys != required_tags:
                to_terminate.append(ins['InstanceId'])

    client.stop_instances(InstanceIds=to_terminate)
