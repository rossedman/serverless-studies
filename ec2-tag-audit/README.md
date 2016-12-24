# EC2 Tag Audit

This lambda takes a list of required tags and audits all resources against this list.
If resources do not meet the tagging standards, the EC2 instances are terminated.

## Use Cases

In a highly enabled DevOps environment this could be used to enforce governance and tagging 
structures. While this is an extreme case it does show the possibilities of governing and 
auditing infrastructure frequently.

## Deploy

```
./deploy.sh -s KinesisStreamApp -b lambdawhatever425 -o output.yaml
```
