import json
from datetime import datetime, timedelta
import boto3
from dateutil.tz import tzutc

iam = boto3.client('iam')
iam_user = "s3-user"
max_age_of_policy = 10

def lambda_handler(event, context):
    
    try:
        path = event["queryStringParameters"]["path"]
    except Exception:
        path = ""
    
    nowtime = datetime.today()
    
    try:
        response = iam.list_policies(
            Scope='Local',
            OnlyAttached=True,
            MaxItems=500
        )
    except Exception:
        pass
    
    policies = {policy['Arn']: int(1000 * datetime.timestamp(datetime.strptime(str(policy['CreateDate'])[:19],  "%Y-%m-%d %H:%M:%S")))
                for policy in response['Policies']
               }  
    
    arn_paths = {}

    if path != "":
        to_delete = [policy
            for policy in policies
            if 'temporary' in policy
        ]
        
        for policy in to_delete:
            policy_details = iam.get_policy(
                PolicyArn=policy
                )
            
            policy_version = iam.get_policy_version(
                PolicyArn = policy, 
                VersionId = policy_details['Policy']['DefaultVersionId']
                )
            arn_paths[policy] = list(policy_version['PolicyVersion']['Document']['Statement'][0]['Resource'])
         
        to_delete = set()
        
        for arn in arn_paths:
            for blocked_path in arn_paths[arn]:
                if path in blocked_path:
                    to_delete.add(arn)
        
        to_delete = list(to_delete)
        
        if not len(to_delete):
            return f"There are no policies to delete in path: {path}"
            
    else:
        to_delete = [policy
            for policy in policies
            if nowtime - datetime.fromtimestamp(policies[policy] / 1000) >= timedelta(days=max_age_of_policy) and 'temporary' in policy
        ]
        
    if not len(to_delete):
        return "User has no policies which could be removed"

    for policy in to_delete:

        iam.detach_user_policy(
            UserName=iam_user,
            PolicyArn=policy
        )
        
        iam.delete_policy(
            PolicyArn=policy
        )
    
    if path != "":
        return f"Policy which was blocking access in: {path} - has been removed"
    
    if len(to_delete):
        return f"{len(to_delete)} policies older than {max_age_of_policy} days have been removed"
    return "There are no policies to remove"
