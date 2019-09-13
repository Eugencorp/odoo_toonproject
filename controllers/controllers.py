# -*- coding: utf-8 -*-
from odoo import http
import requests
import os

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
            response = requests.put(upload_path + filename + extension, 
                data=data, auth=(login, password))
            return("Got file " + name +'; Result: ' + str(response.status_code));
        return "No files found"
        

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
