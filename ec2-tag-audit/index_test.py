
from datetime import datetime, timedelta
import index as i


def test_parse_compliance_status():

    expiration_past = datetime.now() - timedelta(days=2)
    expiration_future = datetime.now() + timedelta(days=2)

    records = [
        {
            'id': 'i-0c9d6b554167f2bea',
            'tags': [{'Key': 'environment', 'Value': 'stage'}]
        },
        {
            'id': 'i-064529d714f511dbb',
            'tags': [{'Key': 'expiration', 'Value': expiration_past.strftime("%Y-%m-%d %H:%M:%S")}]
        },
        {
            'id': 'i-03f4std714f511dbb',
            'tags': [{
                'Key': 'expiration', 'Value': expiration_future.strftime("%Y-%m-%d %H:%M:%S")
            }]
        },
        {
            'id': 'i-sdf098345kjsdf'
        }
    ]

    expected = {
        'terminate': ['i-064529d714f511dbb'],
        'terminate_soon': ['i-03f4std714f511dbb'],
        'set_expiration': ['i-0c9d6b554167f2bea', 'i-sdf098345kjsdf']
    }

    assert i.parse_compliance_status(records) == expected


def test_validate_tag_keys():
    given_tags = ['environment', 'owner']
    required_tags = ['environment', 'owner']
    assert i.validate_tag_keys(given_tags, required_tags) is True


def test_validate_tag_keys_different():
    given_tags = ['environment']
    required_tags = ['environment', 'owner']
    assert i.validate_tag_keys(given_tags, required_tags) is False


def test_validate_tag_keys_when_has_extras():
    given_tags = ['environment', 'extra']
    required_tags = ['environment']
    assert i.validate_tag_keys(given_tags, required_tags) is True


def test_validate_tag_value():
    given_value = "dev"
    accepted_values = ["dev", "prod", "stage"]
    assert i.validate_tag_value(given_value, accepted_values) is True


def test_audit_tag_value_not_accepted():
    given_value = "whatever"
    accepted_values = ["dev", "stage"]
    assert i.validate_tag_value(given_value, accepted_values) is False


def test_audit_tag_wildcard():
    given_value = "anything"
    accepted_values = ["*"]
    assert i.validate_tag_value(given_value, accepted_values) is True


def test_audit_tag_partial_match():
    given_value = "person@gmail.com"
    accepted_values = ["*@gmail.com"]
    assert i.validate_tag_value(given_value, accepted_values) is True


def test_audit_tag_partial_match_order():
    given_value = "person@gmail.com"
    accepted_values = ["person@*", "whatever", "*@gmail.com"]
    assert i.validate_tag_value(given_value, accepted_values) is True


def test_audit_tags():
    given_tags = [
        {'Value': 'dev', 'Key': 'environment'},
        {'Value': 'person', 'Key': 'owner'}
    ]
    required_tags = {
        'environment': [
            'dev',
            'prod',
            'stage'
        ],
        'owner': ['*']
    }

    assert i.audit_tags(given_tags, required_tags) is True


def test_audit_tags_no_tags():
    given_tags = []
    required_tags = {
        'environment': ['*']
    }

    assert i.audit_tags(given_tags, required_tags) is False


def test_audit_tags_more_then_required():
    given_tags = [
        {'Value': 'dev', 'Key': 'environment'},
        {'Value': 'person', 'Key': 'owner'}
    ]
    required_tags = {
        'environment': ['dev', 'stage']
    }

    assert i.audit_tags(given_tags, required_tags) is True


def test_audit_tags_lots_of_wildcards():
    given_tags = [
        {'Value': 'dev', 'Key': 'environment'},
        {'Value': 'Whatever Name', 'Key': 'person'},
        {'Value': 'person@gmail.com', 'Key': 'email'},
        {'Value': '10930', 'Key': 'costCenter'}
    ]
    required_tags = {
        'environment': ['dev', 'stage'],
        'person': ['Whatever*'],
        'email': ['*@gmail.com']
    }

    assert i.audit_tags(given_tags, required_tags) is True


def test_is_node_first_offense():
    given_tags = ['environment', 'owner']
    assert i.node_first_offense(given_tags) is True


def test_is_node_second_offense():
    given_tags = ['environment', 'owner', 'expiration']
    assert i.node_first_offense(given_tags) is False


def test_node_past_due():
    expiration_date = datetime.now() - timedelta(days=2)
    assert i.node_past_due(
        expiration_date.strftime("%Y-%m-%d %H:%M:%S")) is True
