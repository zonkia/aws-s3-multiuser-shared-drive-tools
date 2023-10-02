1. Create S3 bucket with versioning enabled and add bucket_policy
2. Create IAM policies: s3_user_policy, s3_admin_policy, lambda_policy
3. Create IAM Users (s3_user and s3_admin) and IAM Role for Lambda and attach proper policies.
4. Create 3 Lambda functions and use the same IAM Role
5. Copy/paste python scripts' contents to Lambda functions and replace variables with your values
6. Create Lambda URL for all 3 Lambdas
7. Install and configure AirLiveDrive (recommended for multiuser scenario - 1sec cache settings) and mount S3 as drive in Windows

**To restore objects** in specific directory (example: S3/Dirname/Subdirname/Another dir) use Lambda URL with query string: _restrore.lambda-url.us-east-1.on.aws/?path=Dirname/Subdirname/Another dir_

**To block access for s3_user** in specific directory/file:(example: S3/Dirname/Subdirname/Another dir) use Lambda URL with query _string: lock.lambda-url.us-east-1.on.aws/?path=Dirname/Subdirname/Another dir_
* block Lambda affects only s3_user - policies are not attached to s3_admin user

**To unlock access for s3_user** in specific directory/file:(example: S3/Dirname/Subdirname/Another dir) use Lambda URL with query string: _unlock.lambda-url.us-east-1.on.aws/?path=Dirname/Subdirname/Another dir_
* unlock access Lambda can be used without giving any path parameter to URL or can be triggered by EventBridge schedule - if no paramaters are given this Lambda by default will remove any blocking policies which are older than 10 days (default)
