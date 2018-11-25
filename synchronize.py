#!/usr/bin/env python
#from __future__ import print_function
from __future__ import with_statement
from googleapiclient.discovery import build
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
import time
import os
import sys
import errno
import random
import datetime
import io
import threading
from fuse import FUSE, FuseOSError, Operations

# If modifying these scopes, delete the file token.json.

SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
	creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))


def synchronize2():
	global service
	while(1):
		data=[]
		print "\n\nNew Iteration"
		
		f=open("config.ts","r")
		data=f.readlines();
		f.close()
		data_len=len(data)
		
		f=open("config.ts","w")
		for i in range(0,data_len):
			print i, data[i]
			
			data[i]=data[i].split("||")
			data[i][2]=data[i][2].rstrip("\n")
			filestatus=0
				
			try:
				query = service.files().get(fileId=data[i][1]).execute()
			except Exception as e:
				print "File Not Found : ",e
				filestatus=1
			
			if(filestatus==1):
				print "delete the file &&&&&&&&7"					
			else:
				try:
					last_mod_time=service.files().get(fileId=data[i][1],fields='modifiedTime,name').execute()
					print last_mod_time.get('modifiedTime')
					print data[i][2] 
					if(last_mod_time.get('modifiedTime')!=data[i][2]):
						
						print "Main Functionality"
						os.remove("Hello/"+data[i][0])
						request = service.files().get_media(fileId=data[i][1])
						fh = io.BytesIO()
						fh = io.FileIO("Hello/"+last_mod_time.get('name'), 'wb')
						data[i][0]=last_mod_time.get('name')
						data[i][2]=last_mod_time.get('modifiedTime')
						
						downloader = MediaIoBaseDownload(fh, request)
						done = False
						while done is False:
							status, done = downloader.next_chunk()
							print "Download %d%%." % int(status.progress() * 100)																																																																																																																																																																																																																																																																																																																			
							print "Status : ",status
				except Exception as e:
					print e
			if(filestatus==0):
				f.write(data[i][0]+"||"+data[i][1]+"||"+data[i][2]+"\n")
				print "Writing : ",data[i][0]+"||"+data[i][1]+"||"+data[i][2]+"\n"

		f.close()

				
		print "Sleeping"
		time.sleep(5)
		print "Woke Up"


synchronize2();
