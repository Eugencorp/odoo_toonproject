# -*- coding: utf-8 -*-

from odoo import models, fields, api

class comment_session(models.Model):
    _name = 'toonproject.comment_session'
    _description = 'Data for some comments made by a use for a video file once at some date'

    author = fields.Many2one('res.users', string = 'Автор')
    date = fields.Datetime(string = 'Время создания')
    task = fields.Many2one('toonproject.task', string = 'Задача')
    video_url = fields.Char(string = 'url видеофайла')
    video_date = fields.Datetime(string = 'Версия видеофайла')
    json = fields.Char(string = 'содержание правок')
    log_msg = fields.Many2one('mail.message')
    
    num_comments = fields.Integer(string="комментариев")
    
    def open_sessions(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/toonproject/comment_session?session=' + str(self.id),
            'session': self.id,
            'target': 'new'
        }
        
    def log_to_task_thread(self):
        for rec in self:
            if rec.task and not rec.log_msg:
                msg = 'добавлены комментарии. <a href="/toonproject/comment_session?session='
                msg = msg + str(rec.id)
                msg = msg + '" target="_blank">Смотреть</a>'
                rec.log_msg = rec.task.message_post(body = msg, subtype = 'mt_note')
                if rec.log_msg.author_id != rec.author.partner_id:
                    rec.log_msg.author_id = rec.author.partner_id