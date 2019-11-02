# -*- coding: utf-8 -*-
from odoo import http
import requests
import datetime
from dateutil.parser import parse as parsedate

class Toonproject(http.Controller):

    def get_sessions_json(self, sessions):
        return ""

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
        new_session = http.request.env['toonproject.comment_session'].create({
                'author': current_user.id, 
                'date': datetime.datetime.now(),
                'task': task.id,
                'video_url': task.preview,
                'video_date': got_date
            })
        new_id = new_session[0].id
        prev_sessions_json = self.get_sessions_json(prev_sessions)
        
        return http.request.render('toonproject.commenting',{
            'video_url':task.preview,
            'author_name':current_user.name,
            'author_id':current_user.id,
            'session_id':new_id,
            'prev_json': prev_sessions_json
            })
            
    @http.route('/toonproject/update_comment_session', auth='user', method=['POST', 'GET'], csrf=False)    
    def update_comment_session(self, session, json, video_url, user_id, **kw):
        user = http.request.env.user
        if not user.id == user_id:
            return http.Response("неизвестный пользователь", status = 500)
        comment_session = http.request.env['toonproject.comment_session'].search([('id','=',session)])
        if len(comment_session)==0:
             return http.Response("неизвестная сессия", status = 500)  
        comment_session = comment_session[0]
        if comment_session.author.id != user.id:
            return http.Response("неизвестный пользователь", status = 500)
        if comment_session.video_url != video_url:
            return http.Response("неизвестная сессия", status = 500) 
        comment_session.json = json
        return http.Response("комментарии сохранены", status = 200)
        
    @http.route('/toonproject/comment_session', auth='user', method=['POST', 'GET'], csrf=False)
    def comment_session(self, session):
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
        new_session = http.request.env['toonproject.comment_session'].create({
                'author': user.id,
                'date': datetime.datetime.now(),
                'task': task.id,
                'video_url': video_url,
                'video_date': video_date
            })
        new_id = new_session[0].id
        prev_sessions_json = self.get_sessions_json(prev_sessions)
        return http.request.render('toonproject.commenting',{
            'video_url':video_url,
            'author_name':user.name,
            'author_id':user.id,
            'session_id':new_id,
            'prev_json': prev_sessions_json
            })