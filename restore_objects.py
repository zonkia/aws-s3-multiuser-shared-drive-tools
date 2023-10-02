from datetime import datetime, timedelta
from dateutil.tz import tzutc
import boto3

s3 = boto3.client('s3')
bucket = 'BUCKET-NAME'

def newline_objects(list_name):
    result = ""
    for element in list_name:
        result += "\n"
        result += (bucket + "/" + element)
    return result

def lambda_handler(event, context):

    try:
        prefixValue = event["queryStringParameters"]["path"]
    except Exception:
        prefixValue = ""

    if prefixValue == "":
        return "No path was given in the URL"

    try:
        versions = s3.list_object_versions(Bucket=bucket, Prefix=prefixValue)
        objectWithLatestDeleteMarker = []
        objects = []
        
        try:
            keys_with_timestamps = {version['Key']: datetime.strptime(str(version['LastModified']), "%Y-%m-%d %H:%M:%S+00:00")
                for version in versions["Versions"]
                if version["IsLatest"]
            }
        except Exception:
            keys_with_timestamps = {}
            
        try:
            markers_with_timestamps = {marker['Key']: datetime.strptime(str(marker['LastModified']), "%Y-%m-%d %H:%M:%S+00:00")
                for marker in versions['DeleteMarkers']
                if marker["IsLatest"]
            }
        except Exception:
            markers_with_timestamps = {}
        
        previous_versions_with_timestamps = {}
        for version in versions['Versions']:
            if not version["IsLatest"] and version['Key'] not in previous_versions_with_timestamps:
                previous_versions_with_timestamps[version['Key']] = datetime.strptime(str(version['LastModified']), "%Y-%m-%d %H:%M:%S+00:00")

        keys_to_ignore = []
        for key in keys_with_timestamps:
            for marker in markers_with_timestamps:
                if key.split('/')[-1] == marker.split('/')[-1] and (keys_with_timestamps[key] != markers_with_timestamps[marker] or keys_with_timestamps[key] == markers_with_timestamps[marker]):
                    if keys_with_timestamps[key] <= markers_with_timestamps[marker]:
                        if markers_with_timestamps[marker] - keys_with_timestamps[key] < timedelta(seconds=2):
                            keys_to_ignore.append(marker)

        for marker in markers_with_timestamps:
            for version in previous_versions_with_timestamps:
                if marker.split('/')[-1] == version.split('/')[-1] and (markers_with_timestamps[marker] != previous_versions_with_timestamps[version] or markers_with_timestamps[marker] == previous_versions_with_timestamps[version]):
                    if markers_with_timestamps[marker] <= previous_versions_with_timestamps[version]:
                        if markers_with_timestamps[marker] - previous_versions_with_timestamps[version] < timedelta(seconds=2):
                            keys_to_ignore.append(marker)
        
        if 'DeleteMarkers' in versions:
            markers_keys = [marker['Key'].split('/')[-1]
                for marker in versions['DeleteMarkers']
                if marker['Key'] not in keys_to_ignore and marker['IsLatest'] 
            ]
            
            objectWithLatestDeleteMarker = [{'Key': version['Key'], 'VersionId': version['VersionId']}
                for version in versions['DeleteMarkers']
                if version['Key'].split('/')[-1] in markers_keys and version['IsLatest'] and ".tmp" not in version['Key'] and "~$" not in version['Key'] and "." in version['Key'] and version['Key'] not in keys_to_ignore
                ]
            
            objects = [object['Key']
                for object in objectWithLatestDeleteMarker
                ]

            if len(objectWithLatestDeleteMarker) > 0:
                objects_count = len(objectWithLatestDeleteMarker)
                temp = []
                
                while len(objectWithLatestDeleteMarker) != 0:
                    if len(temp) == 999:
                        s3.delete_objects(
                            Bucket=bucket,
                            Delete={
                                'Objects': temp,
                                'Quiet': True
                            }
                        )
                        temp = []
                    temp.append(objectWithLatestDeleteMarker.pop(0))
                    if len(objectWithLatestDeleteMarker) == 0:
                        s3.delete_objects(
                            Bucket=bucket,
                            Delete={
                                'Objects': temp,
                                'Quiet': True
                            }
                        )

                return f'Success: restored {objects_count} objects in path "{bucket}/{prefixValue}"; full paths to restored objects: \n {newline_objects(objects)}'
                
            else:
                return f'There are no objects which have Delete Marker as their latest version in path "{bucket}/{prefixValue}"'
        else:
            return f'There are no objects which have Delete Marker as their latest version in path "{bucket}/{prefixValue}"'
            
    except Exception as e:
        return f'ERROR while getting objects from path: "{bucket}/{prefixValue}": {e}'
