import json
import boto3

iam = boto3.client('iam')
bucket_name = "bucket_name"

def lambda_handler(event, context):
    try:
        prefixValue = str(event["queryStringParameters"]["path"])
    except Exception:
        prefixValue = ""

    policy_arn = "arn:aws:iam::111111111:policy/blocking-policy"
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
            return "Path can't be empty. Try again"
    for line in lines:
        if line not in policy_document["Statement"][0]["Resource"]:
            return f"There are no policies to delete in path: {prefixValue}"
    
    policy_document["Statement"][0]["Resource"] = [i for i in policy_document["Statement"][0]["Resource"] if i not in lines]
    print(policy_document)

    iam.create_policy_version(
        PolicyArn=policy_arn,
        PolicyDocument=json.dumps(policy_document),
        SetAsDefault=True
        )
    
    iam.delete_policy_version(
        PolicyArn=policy_arn,
        VersionId=policy_version
    )
    
    return f"Policy which was blocking access in: {prefixValue} - has been removed"


        
