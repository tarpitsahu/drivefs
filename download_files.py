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



SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
	creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

def download():
	global service
	root_id="'0AM4f9RkfOJX_Uk9PVA'"
	result_num=1
	filename=[]
	fileid=[]
	query = service.files().list(q=root_id+" in parents").execute()
	for file in query.get('files', []):
			fn=file.get('name')
			fi=file.get('id')

			filename.append(fn)
			fileid.append(fi)
			print "Result Id : ",result_num
			print "File : "+fn+"\nFile Id : "+fi
			print "------------------"
			result_num+=1
	choice=input("Enter The Result Number To DOwnload : ")
	if(choice >=1 and choice <result_num):
		request = service.files().get_media(fileId=fileid[choice-1])
		fh = io.BytesIO()
		fh = io.FileIO("Hello/"+filename[choice-1], 'wb')
		downloader = MediaIoBaseDownload(fh, request)
		done = False
		while done is False:
		    status, done = downloader.next_chunk()
		    print "Download %d%%." % int(status.progress() * 100)



def search():
	global service
	while(1):
		fname=raw_input("\n\n\nEnter a file name to search")
		query = service.files().list(q="name contains '"+fname+"'").execute()
		filenumber=1
		for file in query.get('files', []):
			pathlist=[]
			filename=file.get('name')
			fileid =file.get('id')
			
			while(1):
				try:	
					parentquery = service.files().get(fileId=fileid,fields='parents').execute()
					parentid=parentquery.get('parents')[0]

					namequery = service.files().get(fileId=parentid,fields='name').execute()
					t=namequery.get('name')
					pathlist.append(t)
					fileid=parentid
					print parentid
				except:
					break;
					pass
			pathlist.reverse()
			pathlist.append(filename)
			print "--------"
			print "Result",filenumber, " ==> "
			print "Filename : ",filename
			print "Filepath : ",
			for i in pathlist:
				print i+"/",
			# print query
			print "\n--------"
			filenumber+=1
		


download()