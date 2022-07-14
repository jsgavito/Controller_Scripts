from mcp_functions import *
import pandas as pd 
import json
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request is being made to host')

def gather_info():
    hostip = str(input("What is the MCP IP address? (IPv4 format) "))
    user = str(input("What is the username? "))
    pwd = str(input("What is the password? "))
    host_url = "https://"+ hostip
    #print(host_url)
    return (host_url, user, pwd)
print("This script generates config files (LSPs) for all the tunneles  that are generated on the 3916 devices. managed by an MCP. The config files are stored in ./inventory path.")
#h,u,p = gather_info()
h='https://10.136.76.14'
u='admin'
p='adminpw'
token=authorize_with_MCP(h, u, p)
print('token')
print(token)

NEs_in_MCP=request_equipment(h,token)

inventory=NEs_in_MCP
inventory.pop('links', None)
data=inventory['data']
#formatted_info=json.dumps(data, indent=4)
#print(formatted_info)
#Filtering NEs - 3926
filtered_list=[]
for key in data:
    #print (key)
    NE=[]
    if key['attributes']["networkConstructType"] == "networkElement":
        if key['attributes']['resourceType'] == '3916':
            deviceID=key["id"]
            device_IP=key['attributes']['displayData']["displayIpAddress"]
            deviceType=key['attributes']['resourceType']
            print('IP: ',device_IP, ', DeviceType: ',deviceType, ', NetworkContstructID: ', deviceID)
            NE=[deviceType,deviceID,device_IP]
        else:
            continue
        
    else:
        continue
    filtered_list.append(NE)

print(filtered_list)
#Getting NC_ID for each 3916

ncid_list=[]
for dev in filtered_list:
    for nid in dev:
        nid=str(dev[1])
    ncid_list.append(nid)

##Iterations to get the tunnels

print('Network construct IDs to retrieve:')
print(ncid_list)
freExpectations=[]
filterSet=set()
TunnelBuilder=[]
trail=[]
####Iterar sobre ncid_list para obtener los miembros de cada LSP
### Se va a llamar a una nueva función para obtener el JSON de los LSPs 
### Se hace el filtrado
### Con la información filtrada se puede generar el archivo con configuración para cada nodo
for dev2 in ncid_list:
    y=dev2
    print('Retrieving info from: ', y)
    yy=create_config( h,y,token)
    print(yy)
