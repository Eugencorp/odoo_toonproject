# -*- coding: utf-8 -*-
from odoo import http
import requests
import os
import datetime
from urllib.parse import urlparse
from ftplib import FTP, FTP_TLS
import io


class Toonproject(http.Controller):

    def upload_webdav(self, login, password, url, data):
        response = requests.put(url, data=data, auth=(login, password))
        if response.status_code < 200 or response.status_code > 300:
            return response
    
    def upload_ftp(self, login, password, up_url, data):
        return self.common_ftp(login, password, up_url, data, False)
        
    def upload_ftps(self, login, password, up_url, data):
        return self.common_ftp(login, password, up_url, data, True)        
    
    def common_ftp(self, login, password, up_url, data, FTPS):
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
        if FTPS:
            ftp = FTP_TLS()
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
    
    def check_preview_comments(self, task, readpath):
        comment_sessions = http.request.env['toonproject.comment_session'].search([('task','=', task.id),('video_url','=',readpath)])
        if len(comment_sessions) > 0:
            return True
        return False
        
    def backup_old_preview(self, task, server_fn, login, password, writepath, fullreadpath):
        # download readpath, upload it with new name and replace name in any comment_sessions for task with old preview name 
        comment_sessions = http.request.env['toonproject.comment_session'].search([('task','=', task.id),('video_url','=',fullreadpath)])
        video_date = comment_sessions[0].video_date
        date_suffix = str(video_date).replace(' ','_').replace('-','').replace(':','')[0:-2]
        read_response = requests.get(fullreadpath)
        if read_response.status_code < 200 or read_response.status_code > 300:
            return read_response
        path, name = os.path.split(fullreadpath)
        filename, extension = os.path.splitext(name)
        new_name = filename + "_" + date_suffix + extension
        write_result = server_fn(login, password, writepath + new_name, read_response.content)
        if write_result:
            return write_result
        for session in comment_sessions:
            session.video_url = path + '/' + new_name
        return False
    
    def get_task(self, task_string):
        task_id = int(str.replace(task_string,',',''))
        task = http.request.env['toonproject.task'].search([('id', '=', task_id)])
        return task
    
    def get_server_info(self, kw, param_type):
        pr = None
        ss = None
        if kw.get('task') or kw.get('t'):
            task = self.get_task(kw.get('task') or kw.get('t'))
            if task:
                pr = task.price_record
                
        if kw.get('price'):
            price_string = kw.get('price')
            price_id = int(str.replace(price_string,',',''))
            pr = http.request.env['toonproject.price'].search([('id', '=', price_id)]) 

        if kw.get('setting'):
            setting_string = kw.get('setting')
            setting_id = int(str.replace(setting_string,',',''))
            ss = http.request.env['toonproject.fileserver_setting'].search([('id', '=', setting_id)])            

        if pr:
            if param_type == 'preview' and not pr.preview_server_setting:
                return pr.preview_login, pr.preview_password, pr.preview_upload_path, pr.preview_path
                
            if param_type == 'mainsource' and not pr.mainsource_server_setting:
                return pr.mainsource_login, pr.mainsource_password, pr.mainsource_upload_path, pr.mainsource_path
                
            if param_type == 'preview':
                ss = pr.preview_server_setting            
            if param_type == 'mainsource':
                ss = pr.mainsource_server_setting
                
        if not ss:
            return None, None, None, None
            
        login = ss.login
        password = ss.password
        upload_root = ss.upload_root
        external_root = ss.external_root            
        if upload_root[-1] != '/':
            upload_root = upload_root + '/'
        if external_root[-1] != '/':
            external_root = external_root + '/'             
        subfolder = ''
        
        if pr:
            if param_type == 'preview':
                subfolder = pr.preview_subfolder or ''
            if param_type == 'mainsource':
                subfolder = pr.mainsource_subfolder or ''               
            if param_type == 'preview' and pr.preview_custom_user:
                login = pr.preview_login
                password = pr.preview_password     
            if param_type == 'mainsource' and pr.mainsource_custom_user:
                login = pr.mainsource_login
                password = pr.mainsource_password

        if subfolder != '' and subfolder[-1] != '/':
            subfolder = subfolder + '/'   
        upload_path = upload_root + subfolder
        preview_path = external_root + subfolder                
          
        return login, password, upload_path, preview_path            


    
    def eval_upload_and_check(self, kw, server_fn):
        upload_purpose = kw.get('purpose')
        testing_mode = kw.get('price') or kw.get('setting')
        login, password, writepath, readpath  = self.get_server_info(kw, upload_purpose)
        if not writepath or not login or not password:
            return http.Response("Не могу получить информацию о сервере для загрузки", status=500)
        if not readpath:
            return http.Response("Не могу получить http-адрес для чтения файла после загрузки", status=500)            
        filename = "dummy"
        extension = ".txt"
        data = datetime.datetime.now().ctime()
        task = None
        if kw.get('uploaded_file'):
            file = kw.get('uploaded_file')
            name = file.filename
            data = file.read()
            filename, extension = os.path.splitext(name)
            if kw.get('task'):
                task = self.get_task(kw.get('task'))
                if upload_purpose:                
                    if task and task.preview_filename:
                        filename = task.preview_filename
        fullreadpath = readpath + filename + extension
        if task and upload_purpose == 'preview':
            read_response = requests.head(fullreadpath)
            if read_response.status_code >= 200 and read_response.status_code < 300:
                if self.check_preview_comments(task, fullreadpath):
                    backup_result = self.backup_old_preview(task, server_fn, login, password, writepath, fullreadpath)
                    if backup_result:
                        return backup_result
        write_result = server_fn(login, password, writepath + filename + extension, data)
        if write_result:
            return write_result
                
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
            if kw.get('task'):
                if upload_purpose == 'preview': 
                    task.preview = fullreadpath
                elif upload_purpose == 'mainsource':
                    task.mainsource = fullreadpath
            return http.Response(fullreadpath, status=200);
        return http.Response("No files found", status=500)
            
    @http.route('/toonproject/default_preview', auth='user', method=['POST', 'GET'], csrf=False)    
    def default_preview(self, **kw):
        t = kw.get('t')
        if not t:
            return http.Response("Неизвестная задача", status=500)
        task = self.get_task(t)
        if not task.preview_filename:
            return http.Response("Не настроено дефолтное имя для файла", status=500)
        login, password, writepath, readpath  = self.get_server_info(kw, 'preview')
        if not readpath:
            return http.Response("Не настроен дефолтный путь к файлу preview", status=500)
        fullpath = readpath + task.preview_filename + ".mp4"
        responce = requests.head(fullpath)
        if responce.status_code < 200 or responce.status_code >= 300:
            return http.Response("Не обнаружен файл " + fullpath, status=500)
        task.preview = fullpath
        return http.Response(fullpath, status=200)

    @http.route('/toonproject/default_mainsource', auth='user', method=['POST', 'GET'], csrf=False) 
    def default_mainsource(self, t, **kw):
        task = self.get_task(t)
        if not task.preview_filename:
            return http.Response("Не настроено дефолтное имя для файла", status=500)
        if not task.price_record or not task.price_record.mainsource_path:
            return http.Response("Не настроен дефолтный путь к файлу исходника", status=500)
        if not task.price_record.mainsource_ext:
            return http.Response("Не настроено дефолтное расширение для исходников по этому цеху", status=500)            
        fullpath = task.price_record.mainsource_path + task.preview_filename + task.price_record.mainsource_ext
        responce = requests.head(fullpath)
        if responce.status_code < 200 or responce.status_code >= 300:
            return http.Response("Не обнаружен файл " + fullpath, status=500)
        task.mainsource = fullpath
        return http.Response(fullpath, status=200)


    @http.route('/toonproject/webdav', auth='user', method=['POST', 'GET'], csrf=False)
    def webdav(self, **kw):
        return self.eval_upload_and_check(kw, self.upload_webdav)

    @http.route('/toonproject/ftps', auth='user', method=['POST', 'GET'], csrf=False)
    def ftps(self, **kw):
        return self.eval_upload_and_check(kw, self.upload_ftps)

    @http.route('/toonproject/ftp', auth='user', method=['POST', 'GET'], csrf=False)
    def ftp(self, **kw):
        return self.eval_upload_and_check(kw, self.upload_ftp)
        
    @http.route('/toonproject/playlist', auth='user', method=['POST', 'GET'], csrf=False)    
    def playlist(self, current, **kw):
        if not current:
            return http.Response("Not enough parameters", status=404)
        step = kw.get('step')
        start = kw.get('start')
        finish = kw.get('finish')            
        if start: 
            start = int(start)
        if finish:
            finish = int(finish)            
        current = int(str.replace(current,',',''))
        if step:
            step = int(step)
        current_scene = http.request.env['toonproject.asset'].search([('id','=', current)])
        if not current_scene:
            return http.Response("No asset found", status=404)
        type = current_scene.assettype_id
        project = current_scene.project_id
        all_scenes = http.request.env['toonproject.asset'].search([('project_id','=', project.id),('assettype_id','=',type.id)])
        if not step and not start:
            start = all_scenes[0].id
        if not step and not finish:
            finish = all_scenes[len(all_scenes)-1].id
        if not step:
            if not start in all_scenes.ids or not finish in all_scenes.ids:
                return http.Response("Start or finish ids not in same project or not of same type", status=404)                
        else:
            for i in range(len(all_scenes)):
                if all_scenes[i].id == current:
                    ns = i - step
                    if ns < 0:
                        ns = 0
                    start = all_scenes[ns].id
                    nf = i + step
                    if nf >= len(all_scenes):
                        nf = len(all_scenes)-1
                    finish = all_scenes[nf].id
                    break
        
        r = False
        active_id = 0
        playlist_array = []
        previous_file = False
        for scene in all_scenes:
            if scene.id == start:
                r = True
            if r:
                new_item = {'name': scene.name, 'sources':[{'src': scene.last_preview}]}
                if scene.last_preview: 
                    if scene.last_preview != previous_file:                    
                        playlist_array.append(new_item)
                        previous_file = scene.last_preview
                    elif scene.id == current:
                        playlist_array.pop()
                        playlist_array.append(new_item)
            if scene.id == current:
                active_id = len(playlist_array)-1
            if scene.id == finish:
                break
            
        
        return http.request.render('toonproject.playlist',{'active_id':active_id, 'playlist_array':playlist_array})        

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
