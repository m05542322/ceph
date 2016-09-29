import os
import boto
import boto.s3.connection
from pprint import pprint
import json

#env = 'KH_Ceph'
env = 'FET_Ceph'

with open('etc/config.json', 'r') as f:
    config = f.read()
f.close()

config = json.loads(config)

access_key = config[env]['access_key']
secret_key = config[env]['secret_key']
host = config[env]['host']

conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = host,
        # uncomment if you are not using ssl
        is_secure=False,
        calling_format = boto.s3.connection.OrdinaryCallingFormat()
)

#pprint(vars(conn));

def listBuckets():
        buckets = conn.get_all_buckets()
        return buckets
        #for bucket in conn.get_all_buckets():
        #        print "{name}\t{created}".format(
        #                name = bucket.name,
        #                created = bucket.creation_date,
        #        )



def listObjectsInBucket(bucketName):        
        try:
                bucket = conn.get_bucket(bucketName);
                bucket_list = bucket.list()
                status=1
                return status, bucket_list
                '''
                for key in bucket.list():
                        #pprint (vars(key))
                        #pprint(vars(key.bucket))
                        #print key.bucket.name
                        print "{name}\t{size}\t{modified}".format(
                                name = key.name,
                                size = key.size,
                                modified = key.last_modified,
                        )
                '''
        except boto.exception.S3ResponseError as err:
                status = 0
                return status, err
                '''
                print "Status Code: {status}\nMessage: {message}".format(
                        status = err.status,
                        message = err.message
                )
                '''
def createObjectFromFile(bucketName, fileName, file):
    #print fileName
    try: 
        bucket = conn.get_bucket(bucketName);
        key = bucket.new_key(fileName)
        try:
            key.set_contents_from_string(file.read())
            status = 1
            return status
            #pprint(vars(conn))
        except IOError as err:
            status = 0
            #print err
            return status, err
    except boto.exception.S3ResponseError as err:
        #pprint(vars(err))
        status = 0
        return status, err

#print(createObjectFromFile('my-new-bucket2', 'python_ceph.tar.gz'))

#listBuckets()

#print "\r"

#listObjectsInBucket('my-new-bucket2-1')

