# Kinesis Stream 

This is a serverless application that users Lambda functions to document when S3
Objects are created into a DynamoDB table. When objects are created a signed URL
is generated and stored alongside the object metadata. When objects are deleted they
are removed from the table.

## Deploy

```
./deploy.sh -s KinesisStreamApp -b lambdawhatever425 -o output.yaml
```
