# -*- coding: utf-8 -*-
from odoo import http
import requests
import os
import datetime
from urllib.parse import urlparse
from ftplib import FTP
import io


class Toonproject(http.Controller):

    def upload_webdav(self, login, password, url, data):
        response = requests.put(url, data=data, auth=(login, password))
        if response.status_code < 200 or response.status_code > 300:
            return response
    
    def upload_ftp(self, login, password, up_url, data):
        if type(data) == str:
            data = str.encode(data)
        bio = io.BytesIO(data)
        upload_parts = urlparse(up_url)
        url = upload_parts.netloc.split(':')
        host = url[0]
        port = 21
        if len(url)>1:
            port = int(url[1])
        path = upload_parts.path
        if path and path[0] == '/':
            path = path[1:]
        path, filename = os.path.split(path)
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
            
        ftp.storbinary('STOR '+ filename, bio)
        ftp.close()
        
    
    def get_task(self, task_string):
        task_id = int(str.replace(task_string,',',''))
        task = http.request.env['toonproject.task'].search([('id', '=', task_id)])
        return task
    
    def get_server_info(self, kw, param_type):
        pr = None
        if kw.get('task'):
            task = self.get_task(kw.get('task'))
            if task:
                pr = task.price_record
                
        if kw.get('price'):
            price_string = kw.get('price')
            price_id = int(str.replace(price_string,',',''))
            pr = http.request.env['toonproject.price'].search([('id', '=', price_id)])            

        if pr:
            if param_type == 'preview':
                return pr.preview_login, pr.preview_password, pr.preview_upload_path, pr.preview_path
        else:
            return None, None, None, None
    
    def eval_upload_and_check(self, kw, server_fn):
        upload_purpose = 'preview'
        testing_mode = kw.get('price')
        login, password, writepath, readpath  = self.get_server_info(kw, upload_purpose)
        if not writepath or not login or not password:
            return http.Response("Не могу получить информацию о сервере для загрузки", status=500)
        if not readpath:
            return http.Response("Не могу получить http-адрес для чтения файла после загрузки", status=500)            
        filename = "dummy"
        extension = ".txt"
        data = datetime.datetime.now().ctime()
        if kw.get('uploaded_file'):
            file = kw.get('uploaded_file')
            name = file.filename
            data = file.read()
            filename, extension = os.path.splitext(name)
            if upload_purpose == 'preview' and kw.get('task'):
                task = self.get_task(kw.get('task'))
                if task and task.preview_filename:
                    filename = task.preview_filename
        write_result = server_fn(login, password, writepath + filename + extension, data)
        if write_result:
            return write_result
        fullreadpath = readpath + filename + extension        
        if testing_mode:
            read_response = requests.get(fullreadpath)
            if read_response.status_code < 200 or read_response.status_code > 300:
                return read_response
            result = read_response.content.decode("utf-8")
            if result == data:
                return http.Response("Все зашибись!", status=200); 
            else:
                return http.Response("Тестовый файл благополучно отправлен, но по внешнему адресу не доступен", status=500)
        else:
            if upload_purpose == 'preview' and kw.get('task'):
                task.preview = fullreadpath
            return http.Response(fullreadpath, status=200);
        return http.Response("No files found", status=500)
            


    @http.route('/toonproject/webdav', auth='user', method=['POST', 'GET'], csrf=False)
    def webdav(self, **kw):
        return self.eval_upload_and_check(kw, self.upload_webdav)



    @http.route('/toonproject/ftp', auth='user', method=['POST', 'GET'], csrf=False)
    def ftp(self, **kw):
        return self.eval_upload_and_check(kw, self.upload_ftp)
        

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
