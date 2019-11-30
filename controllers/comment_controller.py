# -*- coding: utf-8 -*-
from odoo import http
import requests
import datetime
from dateutil.parser import parse as parsedate
import json 

class Toonproject(http.Controller):

    def get_sessions_json(self, sessions):
        comments = []
        for session in sessions:
            json_string = session.json
            if json_string:
                data = json.loads(json_string)
                for comment in data:
                    if 'is_new' in comment:
                        del comment['is_new']
                    comment['date'] = session.date.strftime("%d %b %H:%M")
                    comments.append(comment)
        return comments

    @http.route('/toonproject/comment', auth='user', method=['POST', 'GET'], csrf=False)    
    def comment(self, t, **kw):
        task = http.request.env['toonproject.task'].search([('id', '=', int(str.replace(t,',','')))])
        if not task:
            return http.Response("Не найдено задания с идентификатором " + t, status=200)
        if not task.preview:
             return http.Response("Не найдено видео-preview для задания с идентификатором " + t, status=200)                 
        video_info = requests.head(task.preview)
        if video_info.status_code < 200 or video_info.status_code >= 300:
            return http.Response("Не найден видеофайл по адресу " + video_info, status=200)
        got_string_date = video_info.headers['Last-Modified']
        got_date = parsedate(got_string_date)
        current_user = http.request.env.user
        #check user rights maybe here
        prev_sessions = http.request.env['toonproject.comment_session'].search([('task','=',task.id),('video_date','=',got_date)])
        new_id = 0
        prev_sessions_json = self.get_sessions_json(prev_sessions)
        
        return http.request.render('toonproject.commenting',{
            'video_url':task.preview,
            'author_name':current_user.name,
            'author_id':current_user.id,
            'session_id':new_id,
            'prev_json': prev_sessions_json,
            'task_id': task.id
            })
                       
    @http.route('/toonproject/update_comment_session', auth='user', method=['POST', 'GET'], csrf=False)    
    def update_comment_session(self, session, task, json_string, video_url, user_id, **kw):
        user_id = int(str.replace(user_id,',',''))
        session = int(str.replace(session,',',''))
        task = int(str.replace(task,',',''))
        user = http.request.env.user
        if not user.id == user_id:
            return http.Response("неизвестный пользователь", status = 500)
        
        video_info = requests.head(video_url)
        if video_info.status_code < 200 or video_info.status_code >= 300:
            return http.Response("Не найден видеофайл по адресу " + video_url, status=500)
        got_string_date = video_info.headers['Last-Modified']
        got_date = parsedate(got_string_date)        
        comment_session = http.request.env['toonproject.comment_session'].search([('id','=',session)])
        if len(comment_session)==0:
            comment_session = http.request.env['toonproject.comment_session'].create({
                'author': user.id, 
                'date': datetime.datetime.now(),
                'task': task,
                'video_url': video_url,
                'video_date': got_date
            })  
            if comment_session and len(comment_session):
                comment_session[0].log_to_task_thread()
        comment_session = comment_session[0]
        #data = json.loads(json_string) 
        comment_session.json = json_string
        if kw.get('num'):
            comment_session.num_comments = int(kw.get('num'))
        return http.Response(str(comment_session.id), status = 200)
        
    @http.route('/toonproject/comment_session', auth='user', method=['POST', 'GET'], csrf=False)
    def comment_session(self, session,  **kw):
        user = http.request.env.user
        if type(session) == str:
            session = int(str.replace(session,',',''))
        the_session = http.request.env['toonproject.comment_session'].search([('id', '=', session)])
        if len(the_session)==0:
             return http.Response("неизвестная сессия", status = 500)
        the_session = the_session[0]
        video_url = the_session.video_url
        video_date = the_session.video_date
        task = the_session.task
        prev_sessions = http.request.env['toonproject.comment_session'].search([('task','=',task.id),('video_date','=',video_date)])
        new_id = 0
        prev_sessions_json = self.get_sessions_json(prev_sessions)
        return http.request.render('toonproject.commenting',{
            'video_url':video_url,
            'author_name':user.name,
            'author_id':user.id,
            'session_id':new_id,
            'prev_json': prev_sessions_json,
            'task_id': task.id
            })