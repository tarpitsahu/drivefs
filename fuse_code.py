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
		# print "\n\nNew Iteration"
		
		f=open("config.ts","r")
		data=f.readlines();
		f.close()
		data_len=len(data)
		
		f=open("config.ts","w")
		for i in range(0,data_len):
			# print i, data[i]
			
			data[i]=data[i].split("||")
			data[i][2]=data[i][2].rstrip("\n")
			filestatus=0
				
			try:
				query = service.files().get(fileId=data[i][1]).execute()
			except Exception as e:
				print "File Not Found : ",e
				filestatus=1
			
			if(filestatus==1):
				print "delete the file"
				os.remove("Hello/"+data[i][0])			
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
				except Exception as e:
					print e
			if(filestatus==0):
				f.write(data[i][0]+"||"+data[i][1]+"||"+data[i][2]+"\n")
				print "Writing : ",data[i][0]+"||"+data[i][1]+"||"+data[i][2]+"\n"

		f.close()

				
		print "Sleeping"
		time.sleep(5)
		print "Woke Up"


def synchronize():
	print "Synchronization Started"
	global service
	while(1):
		listoffiles=os.listdir("Hello")
		if("download_file" in listoffiles):
			listoffiles.remove("download_file")
		for i in listoffiles:
			query = service.files().list(q="name='"+i+"'").execute()
			if(len(query.get('files',[]))==0):
				print "Trashing : ", i
				os.rename("Hello/"+i,"trash/"+i)
		time.sleep(60)

def download():
	global service
	while(1):
		fname=raw_input("Enter a file name to search")
		query = service.files().list(q="name contains '"+fname+"'").execute()
		for file in query.get('files', []):
			filename=file.get('name')
			print filename
					





class Passthrough(Operations):
	


	def __init__(self, root):
		print "Initializing Root"
		self.root = root

	# Helpers
	# =======

	def _full_path(self, partial):
		if partial.startswith("/"):
			partial = partial[1:]
		path = os.path.join(self.root, partial)
		return path

	# Filesystem methods
	# ==================

	def access(self, path, mode):
		global service
		print "Access Called : ", path 
		full_path = self._full_path(path)
		
		if not os.access(full_path, mode):
			raise FuseOSError(errno.EACCES)

	def chmod(self, path, mode):
		# print "Chmod Called"
		full_path = self._full_path(path)
		return os.chmod(full_path, mode)

	def chown(self, path, uid, gid):
		# print "Chown Called"
		full_path = self._full_path(path)
		return os.chown(full_path, uid, gid)

	def getattr(self, path, fh=None):
		print "getattr called"
		full_path = self._full_path(path)
		st = os.lstat(full_path)
		return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
					 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

	def readdir(self, path, fh):
		# print "readdir called"
		full_path = self._full_path(path)

		dirents = ['.', '..']
		if os.path.isdir(full_path):
			dirents.extend(os.listdir(full_path))
		for r in dirents:
			yield r

	def readlink(self, path):
		# print "read link called"
		pathname = os.readlink(self._full_path(path))
		if pathname.startswith("/"):
			# Path name is absolute, sanitize it.
			return os.path.relpath(pathname, self.root)
		else:
			return pathname

	def mknod(self, path, mode, dev):
		# print "mknod called"
		return os.mknod(self._full_path(path), mode, dev)

	def rmdir(self, path):
		print "rmdir called"
		full_path = self._full_path(path)
		return os.rmdir(full_path)

	def mkdir(self, path, mode):
		# print "------------------------",path
		global service
		file_metadata ={
    		'name' : path.lstrip("/"),
    		'mimeType' : 'application/vnd.google-apps.folder'
		}
		file = service.files().create(body=file_metadata,fields='id').execute()
		print "mkdir called"
		return os.mkdir(self._full_path(path), mode)

	def statfs(self, path):
		full_path = self._full_path(path)
		stv = os.statvfs(full_path)
		return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
			'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
			'f_frsize', 'f_namemax'))

	def unlink(self, path):
		return os.unlink(self._full_path(path))

	def symlink(self, name, target):
		return os.symlink(target, self._full_path(name))

	def rename(self, old, new):
		global service
		print "Old Name : ", old
		print "New Name : ", new
		f=open("config.ts","r")
		data=f.readlines();
		f.close()	
		data_len=len(data)	
		try:
			for i in range(0,data_len):			
				data[i]=data[i].split("||")
				data[i][2]=data[i][2].rstrip("\n")
				if(data[i][0]==old.lstrip('/')):
					recordtomodify=i
					print "RtM", recordtomodify

				if(data[i][0]==new.lstrip('/')):
					recordtoupdate=i
		except Exception as e:
			print "Rename Error"
			print e;	



		if('.Trash-' in new):
			print "Deletion Called"
			# try:
				# query = service.files().list(q="name='"+old.lstrip('/')+"'").execute()
				# for file in query.get('files', []):
				# 	fileid=file.get('id')
					
				# service.files().delete(fileId=data[recordtomodify]).execute()
				
			# except Exception as e:
			try:	# print e
				type(recordtomodify)
				service.files().delete(fileId=data[recordtomodify][1]).execute()
				f=open("config.ts","w")
				for i in range(0,data_len):
					if(i!=recordtomodify):
						f.write(data[i][0]+"||"+data[i][1]+"||"+data[i][2]+"\n")
				f.close()
			except Exception as e:
				print e


		else:
			print "Rename called"
			try:
				query = service.files().list(q="name='"+old.lstrip('/')+"'").execute()
				for file in query.get('files', []):
					fileid=file.get('id')
					print fileid
					
					renamefile = {'name': new.lstrip('/')}
					service.files().update(fileId=fileid,body=renamefile).execute()
					data[recordtomodify][0]=new.lstrip('/')

					break;
			except Exception as e:
				print e

			f=open("config.ts","w")
			for i in range(0,data_len):
					f.write(data[i][0]+"||"+data[i][1]+"||"+data[i][2]+"\n")
			f.close()

		rename_status=os.rename(self._full_path(old), self._full_path(new))

		if('.goutputstream' in old):
			print "Updating content"
			query = service.files().list(q="name='"+new.lstrip('/')+"'").execute()
			for file in query.get('files', []):
					fileid=file.get('id')
					print "Deleting ",fileid
					try:	
						service.files().delete(fileId=fileid).execute()
						body = {'name': new.lstrip('/')}
						media_body = MediaFileUpload("Hello/"+new.lstrip('/'))
						newid=service.files().create(body=body, media_body=media_body).execute()
						data[recordtoupdate][1]=newid.get('id')

					except Exception as e:
						print e
					print "hello hi bye bye"
					try:
						f=open("config.ts","w")
						for i in range(0,data_len):
								f.write(data[i][0]+"||"+data[i][1]+"||"+data[i][2]+"\n")
						f.close()
					except Exception as e:
						print e
					break;

		return rename_status

	def link(self, target, name):
		return os.link(self._full_path(name), self._full_path(target))

	def utimens(self, path, times=None):
		return os.utime(self._full_path(path), times)

	# File methods
	# ============

	def open(self, path, flags):
		print "Opening A File"
		full_path = self._full_path(path)
		return os.open(full_path, flags)

	def insert_file(self,service, title, description,mime_type, filename,fullpath):
		
		print "Welcome to Insert Function : ",filename
		
		print"3.5"
		# body = {'name': filename,'title': title,'description': description,'mimeType': mime_type}
		body = {'name': filename,'title': title,'description': description}
		print "3.6"
		# media_body = MediaFileUpload(filename, mimetype=mime_type)
		
		media_body = MediaFileUpload(filename)
		
		print "******************************", fullpath
		print "4"
		# Set the parent folder.
		fiahl = service.files().create(body=body, media_body=media_body).execute()
		print "##############",fiahl.get('id')	
		lasttime=service.files().get(fileId=fiahl.get('id'),fields='modifiedTime').execute()
		print lasttime.get('modifiedTime')
		print "uploaded"

		f=open("config.ts","a")
		data=filename+"||"+fiahl.get('id')+"||"+lasttime.get('modifiedTime')+"\n"
		f.write(data)
		f.close()


	def create(self, path, mode, fi=None):
		print "Creating A file"
		global service
		full_path = self._full_path(path)
		
		filename = path
		filename=filename.lstrip('/')
		
		print path
		print full_path
		print filename

		title = '"title": "MyTestFile_A.png"'
		description = 'Test Image'
		mime_type = 'application/vnd.google-apps.folder'
	
		print "1"
		status=os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)
		
		print "2"
		try:
			self.insert_file(service, title, description,mime_type, filename, full_path)
		except Exception as e:
			print e

		print "3"
		return status
		#printhi()
		

	def printhi():
		print "Welcome Back"
		
		

	def read(self, path, length, offset, fh):
		print "Reading A file : ",path
		os.lseek(fh, offset, os.SEEK_SET)
		return os.read(fh, length)

	def write(self, path, buf, offset, fh):
		print "Writing A file"			
		os.lseek(fh, offset, os.SEEK_SET)
		return os.write(fh, buf)

	def truncate(self, path, length, fh=None):
		print "Truncating A file"			
		full_path = self._full_path(path)
		with open(full_path, 'r+') as f:
			f.truncate(length)

	def flush(self, path, fh):
		print "Flushing A File"
		return os.fsync(fh)

	def release(self, path, fh):
		print "Releasing A file"		
		return os.close(fh)

	def fsync(self, path, fdatasync, fh):
		print "Syncing A file"		
		return self.flush(path, fh)


def main(mountpoint, root):
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	
	# Call the Drive v3 API
	# results = service.files().list(
	# 	pageSize=10, fields="nextPageToken, files(id, name)").execute()
	# items = results.get('files', [])

	# if not items:
	# 	print 'No files found.'
	# else:
	# 	print 'Files:'
	# 	for item in items:
	# 		print u'{0} ({1})'.format(item['name'], item['id'])


	sync_thread = threading.Thread(target=synchronize2)	
	# download_thread= threading.Thread(target=download)		
	sync_thread.start()
	# download_thread.start()
	try:
		FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True, nonempty=True)
		
		while 1:
			pass
	except Exception as e:
		print e



	# while 1:	
	# 	print "Hello world"
	

if __name__ == '__main__':
	main(sys.argv[2], sys.argv[1])
