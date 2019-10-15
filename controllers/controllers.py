# -*- coding: utf-8 -*-
from odoo import http
import requests
import os
import datetime
from urllib.parse import urlparse
from ftplib import FTP
import io


class Toonproject(http.Controller):
    @http.route('/toonproject/webdav', auth='user', method=['POST', 'GET'], csrf=False)
    def webdav(self, **kw):
        file = kw.get('uploaded_file')
        task_string = kw.get('task')
              
        
        if file and task_string:
            name = file.filename
            data = file.read() 
            task_id = int(str.replace(task_string,',',''))
            task = http.request.env['toonproject.task'].search([('id', '=', task_id)])
            login = task.price_record.preview_login
            password = task.price_record.preview_password
            upload_path = task.price_record.preview_upload_path
            filename, extension = os.path.splitext(name)
            if task.preview_filename:
                filename = task.preview_filename
            readpath = task.price_record.preview_path + filename + extension
  
            response = requests.put(upload_path + filename + extension, 
                data=data, auth=(login, password))
            if response.status_code >= 200 and response.status_code < 300:
                task.preview = readpath
                return(readpath);

        
        elif kw.get('price'):
            price_string = kw.get('price')
            price_id = int(str.replace(price_string,',',''))
            price = http.request.env['toonproject.price'].search([('id', '=', price_id)])
            login = price.preview_login
            password = price.preview_password
            upload_path = price.preview_upload_path 
            read_path = price.preview_path
            
            filename = 'dummy'
            extension = '.txt'
            data = datetime.datetime.now().ctime()

            response = requests.put(upload_path + filename + extension, 
                data=data, auth=(login, password))
            
            if response.status_code < 200 or response.status_code > 300:
                return response
            
            read_file = read_path + filename + extension
            read_response = requests.get(read_file)
            if read_response.status_code < 200 or read_response.status_code > 300:
                return read_response            
            result = read_response.content.decode("utf-8")
            if result == data:
                return http.Response("Все зашибись!", status=200); 
            else:
                return http.Response("Тестовый файл благополучно отправлен, но по внешнему адресу не доступен", status=500)
        
        return http.Response("No files found", status=500)


    @http.route('/toonproject/ftp', auth='user', method=['POST', 'GET'], csrf=False)
    def ftp(self, **kw):
        file = kw.get('uploaded_file')
        task_string = kw.get('task')
              
        
        if file and task_string:
            name = file.filename
            data = file.read() 
            task_id = int(str.replace(task_string,',',''))
            task = http.request.env['toonproject.task'].search([('id', '=', task_id)])
            login = task.price_record.preview_login
            password = task.price_record.preview_password
            upload_path = task.price_record.preview_upload_path
            filename, extension = os.path.splitext(name)
            if task.preview_filename:
                filename = task.preview_filename
            readpath = task.price_record.preview_path + filename + extension
            
            bio = io.BytesIO(data)
            
            upload_parts = urlparse(upload_path)
            url = upload_parts.netloc.split(':')
            host = url[0]
            port = 21
            if len(url)>1:
                port = int(url[1])
            path = upload_parts.path
            if path and path[0] == '/':
                path = path[1:]
            
            ftp = FTP()
            try:
                ftp.connect(host, port, timeout = 10)
            except socket.gaierror:
                return http.Response("Неверный адрес FTP-сервера", status=500)
            except ConnectionRefusedError: 
                return http.Response("FTP-сервер не отвечает", status=500)                
            except socket.timeout:
                return http.Response("FTP-сервер не отвечает", status=500) 
            try:
                ftp.login(login,password)
            except ftplib.error_perm:
                return http.Response("доступ на FTP-сервер запрещен", status=500)  
            try:
                ftp.cwd(path)
            except ftplib.error_perm: 
                return http.Response("неверная папка на FTP-сервере", status=500)
                
            ftp.storbinary('STOR '+ filename + extension, bio)
            ftp.close()
  
            return(readpath);

        
        elif kw.get('price'):
            price_string = kw.get('price')
            price_id = int(str.replace(price_string,',',''))
            price = http.request.env['toonproject.price'].search([('id', '=', price_id)])
            login = price.preview_login
            password = price.preview_password
            upload_path = price.preview_upload_path 
            read_path = price.preview_path
            
            filename = 'dummy'
            extension = '.txt'
            data = datetime.datetime.now().ctime()
            bio = io.BytesIO(str.encode(data))

            upload_parts = urlparse(upload_path)
            url = upload_parts.netloc.split(':')
            host = url[0]
            port = 21
            if len(url)>1:
                port = int(url[1])
            path = upload_parts.path
            if path and path[0] == '/':
                path = path[1:]
                
            ftp = FTP()
            try:
                ftp.connect(host, port, timeout = 10)
            except socket.gaierror:
                return http.Response("Неверный адрес FTP-сервера", status=500)
            except ConnectionRefusedError: 
                return http.Response("FTP-сервер не отвечает", status=500)            
            except socket.timeout:
                return http.Response("FTP-сервер не отвечает", status=500) 
            try:
                ftp.login(login,password)
            except ftplib.error_perm:
                return http.Response("доступ на FTP-сервер запрещен", status=500) 
            try:
                ftp.cwd(path)
            except ftplib.error_perm: 
                return http.Response("неверная папка на FTP-сервере", status=500)                
            
            ftp.storbinary('STOR ' + filename + extension, bio)
            ftp.close()            
            
            read_file = read_path + filename + extension
            read_response = requests.get(read_file)
            if read_response.status_code < 200 or read_response.status_code > 300:
                return read_response            
            result = read_response.content.decode("utf-8")
            if result == data:
                return http.Response("Все зашибись!", status=200); 
            else:
                return http.Response("Тестовый файл благополучно отправлен, но по внешнему адресу не доступен", status=500)
        
        return http.Response("No files found", status=500)
        

# class Toonproject(http.Controller):
#     @http.route('/toonproject/toonproject/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/toonproject/toonproject/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('toonproject.listing', {
#             'root': '/toonproject/toonproject',
#             'objects': http.request.env['toonproject.toonproject'].search([]),
#         })

#     @http.route('/toonproject/toonproject/objects/<model("toonproject.toonproject"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('toonproject.object', {
#             'object': obj
#         })
