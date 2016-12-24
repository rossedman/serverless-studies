
import index as i


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

    assert i.audit_tags(given_tags,required_tags) is True


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
