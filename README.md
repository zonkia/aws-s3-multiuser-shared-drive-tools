1. Create S3 bucket with versioning enabled
2. Create IAM policies: s3_user_policy, s3_admin_policy, lambda_policy
3. Create IAM Users (s3_user and s3_admin) and IAM Role for Lambda and attach proper policies.
4. Create 3 Lambda functions and use the same IAM Role
5. Copy/paste python scripts' contents to Lambda functions and replace variables with your values
6. Create Lambda URL for all 3 Lambdas
7. Install AirLiveDrive (recommended for multiuser scenario) and mount S3 as drive in Windows

**To restore objects** in specific directory (example: S3/Dirname/Subdirname/Another dir/) use Lambda URL with query string: restrore.lambda-url.us-east-1.on.aws**/?path=Dirname/Subdirname/Another dir**

**To block access for s3_user** in specific directory:(example: S3/Dirname/Subdirname/Another dir/) use Lambda URL with query string: lock.lambda-url.us-east-1.on.aws**/?path=Dirname/Subdirname/Another dir**

**To unlock access for s3_user** in specific directory:(example: S3/Dirname/Subdirname/Another dir/) use Lambda URL with query string: unlock.lambda-url.us-east-1.on.aws**/?path=Dirname/Subdirname/Another dir**
