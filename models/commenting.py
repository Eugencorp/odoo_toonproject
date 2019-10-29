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