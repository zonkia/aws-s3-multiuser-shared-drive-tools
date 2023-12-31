1. Create S3 bucket with versioning enabled and add bucket_policy
2. Create gateway VPC endpoint for your S3 bucket
3. Create IAM policies: s3_user_policy, s3_admin_policy, lambda_policy, blocking-policy (blocking-policy must be attached to s3_user)
4. Create IAM Users (s3_user and s3_admin) and IAM Role for Lambda and attach proper policies.
5. Create 3 Lambda functions; restore_objects Lambda can be placed inside your VPC to make use of S3 VPC gateway endpoint - IAM Role will require additional permissions to create ENI; use the same IAM Role for all Lambdas
6. Copy/paste python scripts' contents to Lambda functions and do necessary replacements of variables eg. bucket_name
7. Create public Lambda URLs for all 3 Lambdas
8. Install and configure AirLiveDrive (recommended for multiuser real-time scenario - 1 second cache settings) and mount S3 as drive in Windows
9. Use Lambdas' public URL with paramater 'path' to:

  a) **To restore objects** in specific directory (example: S3/Dirname/Subdirname/Another dir) use Lambda URL with query string: 
  _restrore.lambda-url.us-east-1.on.aws/?path=Dirname/Subdirname/Another dir_

  b) **To block access for s3_user** in specific directory/file:(example: S3/Dirname/Subdirname/Another dir) use Lambda URL with query string: 
  _lock.lambda-url.us-east-1.on.aws/?path=Dirname/Subdirname/Another dir_
  * block Lambda affects only s3_user - blocking-policy is attached to s3_user

  c) **To unlock access for s3_user** in specific directory/file:(example: S3/Dirname/Subdirname/Another dir) use Lambda URL with query string: 
  _unlock.lambda-url.us-east-1.on.aws/?path=Dirname/Subdirname/Another dir_
