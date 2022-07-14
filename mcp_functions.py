import _thread
import json
import ssl
import time

import requests
import websocket
from collections.abc import Iterable
import types
from typing import Any, Dict
import os.path
import pandas as pd 
import json
from progress.bar import Bar


"""
NOTE:

All API Commands must use the Bearer Authorization Header. A token is provided by providing the following info:
  * username
  * password
  * "tenant" set as "master"

These must all be specified in the POST header for the endpoint:

https://{host}/tron/api/v1/tokens

where
  * host =  "https://localdev/externalApi/o1/250/o2/120?md5=YkUzR7VUzz7hWSM0rN8QyA&expires=1569033000&path="
"""


# ************* DEVELOPER NOTE **************************
# * Depending on how you're using this sample code, you may use a MCP ip or a CEC External API Link
# * For CEC users:
# *   - Open your lab info dialog page
# *   - Click the "External API Access" button
# *   - Copy the "External API" link (it should end with "&path=")
# *   - Paste the value in quotes to set the "EXTERNAL_API_LINK" constant in this file
# *   - This link will only work for the duration of your lab, you must repeat this process if you create a new lab
# *
# * For MCP Standalone Users:
# *   - Copy the direct FQDN / IP address of MCP (for example: "https://192.168.1.101")
# *   - Paste the value in quotes to set the "EXTERNAL_API_LINK" constant in this file
# *
# ************** DEVELOPER NOTE **************************
EXTERNAL_API_LINK = "https://10.136.76.14"


"""
Connection info for MCP
Username and password come from the user's personal username and password.
Admin users will have more functionality than non-admin users
"""
host = EXTERNAL_API_LINK
username = "admin"
password = "adminpw"

def authorize_with_MCP(host, username, password):

    path = "/tron/api/v1/tokens"

    # build the URL String
    url = host + path

    auth_payload = "username={uname}&password={passwd}&tenant=master".format(uname=username, passwd=password)
    auth_headers = {"cache-control": "no-cache", "content-type": "application/x-www-form-urlencoded"}

    # TODO Do not use "verify=False" for production applications. Always modify to fit your HTTP certificate model
    response = requests.post(url, data=auth_payload, headers=auth_headers, verify=False)
    data = response.json()

    # return the token from the response json
    return data["token"]

def request_equipment(host, token):
    """
    Find Equipment for a Network Construct
    :param host: MCP Host
    :param network_construct_id: the value of the ID field in an existing Network Construct
    :param token: Authorization token
    :return: The equipment for the referenced Network Construct, or an error if there's no equipment found (INV-21 error)
    """
    path = "/nsi/api/networkConstructs"

    # build the url string
    url = host + path

    auth_headers = {"authorization": "bearer " + token, "cache-control": "no-cache", "content-type": "application/json"}

    # TODO Do not use "verify=False" for production applications. Always modify to fit your HTTP certificate model
    response = requests.get(url, headers=auth_headers, verify=False)
    return response.json()

def request_equipment_by_IP(host, IP, token):
    """
    Find Equipment for a Network Construct
    :param host: MCP Host
    :param network_construct_id: the value of the ID field in an existing Network Construct
    :param token: Authorization token
    :return: The equipment for the referenced Network Construct, or an error if there's no equipment found (INV-21 error)
    """
    path = "/nsi/api/networkConstructs?ipAddress={IP}".format(IP=ip)

    # build the url string
    url = host + path

    auth_headers = {"authorization": "bearer " + token, "cache-control": "no-cache", "content-type": "application/json"}

    # TODO Do not use "verify=False" for production applications. Always modify to fit your HTTP certificate model
    response = requests.get(url, headers=auth_headers, verify=False)
    return response.json()

def get_Tunnels_from_node(host, ncid,token):

    path = "/nsi/api/fres?networkConstruct.id={nw_construct_id}&fields=data.relationships.partitionFres.data&limit=30".format(nw_construct_id=ncid)
    
    # build the url string
    url = host + path

    auth_headers = {"authorization": "bearer " + token, "cache-control": "no-cache", "content-type": "application/json"}

    # TODO Do not use "verify=False" for production applications. Always modify to fit your HTTP certificate model
    response = requests.get(url, headers=auth_headers, verify=False)
    return response.json()


def get_Tunnels_members(host, freE,token):

    path = "/bpocore/market/api/v1/resources/{freExpec}?full=false&obfuscate=true".format(freExpec=freE)
    
    # build the url string
    url = host + path

    auth_headers = {"authorization": "bearer " + token, "cache-control": "no-cache", "content-type": "application/json"}

    # TODO Do not use "verify=False" for production applications. Always modify to fit your HTTP certificate model
    response = requests.get(url, headers=auth_headers, verify=False)
    return response.json()


def get_equipmentIP_by_network_construct(host, ncid, token):
    """
    Find Equipment for a Network Construct
    :param host: MCP Host
    :param network_construct_id: the value of the ID field in an existing Network Construct
    :param token: Authorization token
    :return: The equipment for the referenced Network Construct, or an error if there's no equipment found (INV-21 error)
    """
    path = "/nsi/api/networkConstructs/{network_construct_id}?fields=data.attributes.displayData".format(network_construct_id=ncid)

    # build the url string
    url = host + path

    auth_headers = {"authorization": "bearer " + token, "cache-control": "no-cache", "content-type": "application/json"}

    # TODO Do not use "verify=False" for production applications. Always modify to fit your HTTP certificate model
    response = requests.get(url, headers=auth_headers, verify=False)
    return response.json()


# get equipment for a network construct
#equipment = request_equipment_by_network_construct(host, network_construct_id, token)
#print ("Equipment for NC {id}: {eq}".format(id=network_construct_id, eq=json.dumps(equipment, indent=2)))

def flatten_object(nested: Any, sep: str="_", prefix="") -> Dict[str, Any]:
    """Flattens nested dictionaries and iterables
    
    The key to a leaf (something is not list-like or a dictionary) 
    is the accessors to that leaf from the root separated by sep 
    prefixed with prefix.
    
    If flattening results in a duplicate key raises a ValueError.
    
    For example:
      flatten_object([{'a': {'b': 'c'}}, [1]], 
                     prefix='nest_') == {'nest_0_a_b': 'c', 'nest_1_0': 1}
    """
    ans = {}

    def flatten(x, name=()):
        if isinstance(x, dict):
            for k,v in x.items():
                flatten(v, name + (str(k),))
        elif isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for i, v in enumerate(x):
                flatten(v, name + (str(i),))
        else:
            key = sep.join(name)
            if key in ans:
                raise ValueError(f"Duplicate key {key}")
            ans[prefix + sep.join(name)] = x

    flatten(nested)
    return ans

def create_config( h,NCID,token):
    trail=[]
    df = pd.DataFrame()
    info=get_Tunnels_from_node(h,NCID,token)
    info.pop('meta', None)
    trail=flatten_object(info)
    filterSet=set()

    df=pd.json_normalize(trail, max_level=3)     
    df=df.dropna()
    w=0
    bar = Bar('Loading', fill='@', suffix='%(percent)d%%')
    for col in df.columns:
        if 'included' in col:
            del df[col]
        elif len(col)>25 and '_id' in col:
            #w=w+1
            #print(w)
            t=df[col]
            temp=str(t.values)
            if len(temp)>25 and temp[-10:]=="_transit']":
                #print(temp)
                netc=temp[2:38]
                tunnelname=temp[49:]
                tunnelname=tunnelname[:-10]
                GetIP=get_equipmentIP_by_network_construct(h,netc,token)
                print(' Getting data from: ', GetIP['data']['attributes']['displayData']['displayIpAddress'])
                NE_IP=str(GetIP['data']['attributes']['displayData']['displayIpAddress'])
                hostname=(GetIP['data']['attributes']['displayData']['displayName'])
                file_exists= os.path.exists('inventory/'+hostname+'_'+NE_IP+'.txt')
                if file_exists== True:
                    with open('inventory/'+hostname+'_'+NE_IP+'.txt', 'a+') as file_object:
                        file_object.write("\n")
                        command='gmpls tp-tunnel set ais enable unset bfd'+str(tunnelname)
                        file_object.write(command)
                        w=w+1
                else:
                    filename='inventory/'+hostname+'_'+NE_IP+'.txt'
                    f=open( filename,'w')
                    command='gmpls tp-tunnel set ais enable unset bfd'+str(tunnelname)
                    f.write(command)
                    f.close()
                    w=w+1
                    continue
                #print("This is the IP for ", netc, ":")
                #print()
                #NE_IP=str(GetIP['data']['attributes']['displayData']['displayIpAddress'])
                #print("with tunnel: ", tunnelname )
                filterSet.add(temp)
            else:
                continue
        else:
            del df[col]
            continue
        bar.next()
    bar.finish()
    return_value=str(w)+' command lines were created accross different files'
    return(return_value)
