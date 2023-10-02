from datetime import datetime, timedelta
import boto3
import json
import random
import string

iam = boto3.client('iam')

bucket_name = "bucket_name"
iam_user = "s3-user"

def lambda_handler(event, context):
    nowtime = datetime.today().date()
    
    try:
        prefixValue = str(event["queryStringParameters"]["path"])
    except Exception:
        prefixValue = ""
    

    policy_name = f"temporary-{nowtime}-{''.join(random.choice(string.ascii_letters) for i in range(40))}"
    
    if "." in prefixValue:

        temp_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Action": [
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:GetObject",
                        "s3:GetObjectVersion",
                        "s3:DeleteObjectVersion"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}/{prefixValue}"
                        ]
                }
            ]
        }

    else:
        if prefixValue != "":
            
            temp_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Deny",
                        "Action": [
                            "s3:PutObject",
                            "s3:DeleteObject",
                            "s3:GetObject",
                            "s3:GetObjectVersion"
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{bucket_name}/{prefixValue}/*",
                            f"arn:aws:s3:::{bucket_name}/{prefixValue}"
                            ]
                    }
                ]
            }

        else:
            return str("No path was given in the URL. You need to give path to: \n a) To blocked file: https://address.eu-central-1.on.aws/?path=Drive/Folder/File.txt \n b) OR to blocked directory: https://address.eu-central-1.on.aws/?path=Drive/Folder")

    iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(temp_policy)
    )

    
    iam.attach_user_policy(
        UserName=iam_user,
        PolicyArn=f'arn:aws:iam::<ACC_ID>:policy/{policy_name}'
    )

    return f"Policy was added to block access in: {prefixValue}"


