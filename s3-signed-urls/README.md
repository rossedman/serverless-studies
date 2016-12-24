# S3 Simple Signed URLs

This is a serverless application that users Lambda functions to document when S3
Objects are created into a DynamoDB table. When objects are created, a signed URL
is generated and stored alongside the object metadata. When objects are deleted they
are removed from the table.

## Use Cases

This application is a simple example of what can be done and is not production
ready but here are some ideas that it could be used for.

- *Auditing* - This application could be used to audit users that are updating a
shared bucket. As objects are created, it stores the IP address of where the object
was uploaded from. __No actions are currently logged as objects are deleted__.
- *Download URLs* - This application could be connected with another component
that could send out signed URLs to specific users, only allowing them access to
specific objects in the S3 Bucket.

## Deploy

```
./deploy.sh -s StorageAuditApp -b lambdawhatever425 -o output.yaml
```
