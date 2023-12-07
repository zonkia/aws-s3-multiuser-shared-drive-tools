import boto3
import json

iam = boto3.client('iam')
bucket_name = "bucket_name"

def lambda_handler(event, context):
    
    try:
        prefixValue = str(event["queryStringParameters"]["path"])
    except Exception:
        prefixValue = ""

    policy_arn = "arn:aws:iam::11111111:policy/blocking-policy"
    policy = iam.get_policy(PolicyArn=policy_arn)
    policy_version = policy["Policy"]["DefaultVersionId"]
    policy_document = iam.get_policy_version(
        PolicyArn=policy_arn,
        VersionId=policy_version)["PolicyVersion"]["Document"]
    
    if "." in prefixValue:
        lines = [f"arn:aws:s3:::{bucket_name}/{prefixValue}"]
    else:
        if prefixValue != "":
            lines = [f"arn:aws:s3:::{bucket_name}/{prefixValue}/*"]
        else:
            return "No path was given in the URL. Try again"

    policy_document["Statement"][0]["Resource"] = policy_document["Statement"][0]["Resource"] + lines
    
    iam.create_policy_version(
        PolicyArn=policy_arn,
        PolicyDocument=json.dumps(policy_document),
        SetAsDefault=True
        )

    iam.delete_policy_version(
        PolicyArn=policy_arn,
        VersionId=policy_version
    )
    
    return f"Policy was added to block access in: {prefixValue}"
