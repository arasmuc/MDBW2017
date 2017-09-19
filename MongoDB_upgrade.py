#!/usr/bin/env python

import sys
import requests
import json
import time
import argparse
import subprocess
import pprint
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



realm = "MMS Public API"

def check_arg(args=None):
        parser = argparse.ArgumentParser(description='Script to maitenance MongoDB cluster')
        parser.add_argument('-U', '--user',
                           help='use e-mail address',
                           required='True')
        parser.add_argument('-K', '--key',
                           help='user Ops Manager REST API key',
                           required='True')
        parser.add_argument('-C', '--cluster',
                           help='cluster name from Ops Manager',
                           required='True')
        parser.add_argument('-MMS', '--opsmgr',
                           help='Ops Manager Name',
                           required='True'),
        parser.add_argument('-P', '--port',
                           help='Ops Manager port number',
                           required='True'),
        parser.add_argument('-V', '--version',
                           help='please put your option',
                           choices=['3.4.1-ent','3.4.2-ent','3.4.3-ent','3.4.4-ent','3.4.6-ent','3.4.7-ent','3.4.9-ent'],
                           required='True')


        results = parser.parse_args(args)
        return (results.cluster,results.user,results.key,results.opsmgr,results.port,results.version)


cluster,user,key,opsmgr,port,version=check_arg(sys.argv[1:])
automation='https://'+opsmgr+':'+port+'/api/public/v1.0/groups/%s/automationConfig'


mongoDbVer=[{"builds":[{ "architecture": "amd64",
                    "bits": 64,
                    "flavor": "rhel",
                    "maxOsVersion": "7.0",
                    "minOsVersion": "6.2",
                    "gitVersion": "3f76e40c105fc223b3e5aac3e20dcd026b83b38b",
                    "modules": [
                        "enterprise"
                    ],
                    "platform": "linux",
                    "url": ""
                }], "name": ""}]


def getGroup(clu):
    try:
        r = requests.get('https://'+opsmgr+':'+port+'/api/public/v1.0/groups/byName/%s' % clu, auth=requests.auth.HTTPDigestAuth('%s' % user, '%s' % key), verify=False)
        r.raise_for_status()
        j = r.json()
        return j["id"]
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)



def getJson():
    try:
        r = requests.get(automation % getGroup(cluster), auth=requests.auth.HTTPDigestAuth('%s' % user, '%s' % key), verify=False)
        r.raise_for_status()
        j = r.json()
        return j
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)



def putJson(j):
    try:
        r = requests.put(automation % getGroup(cluster), data=json.dumps(j), headers={'content-type':'application/json'}, auth=requests.auth.HTTPDigestAuth('%s' % user, '%s' % key), verify=False)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)



def ChangeVersion(opsmgr,port,ver):
    j=getJson()
    check=[]
    for version in j["mongoDbVersions"]:
        print version['name']
        check.append(version['name'])
    if ver not in check:
        mongoVer=[]
        v=ver[:5]
        link='https://'+opsmgr+':'+port+'/automation/mongodb-releases/linux/mongodb-linux-x86_64-enterprise-rhel62-'+v+'.tgz'
        for i in mongoDbVer:
            i["builds"][0]['url']=link
            i["name"]=ver
            mongoVer.append(i)
        j["mongoDbVersions"].extend(mongoVer)
    for p in j["processes"]:
         p["version"] = ver
#    for i in j["processes"]:
#       i["featureCompatibilityVersion"]=str(float(ver[:3])-0.2)
    putJson(j)


ChangeVersion(opsmgr,port,version)
