# -*- coding: utf-8 -*-

from odoo import models, fields, api

class afile(models.Model):
    _name = 'toonproject.afile'
    _description = 'File model for uploading additional files'
    
    name = fields.Char(string = "Название")
    external_path = fields.Char(string = "Глобальный путь")
    local_path = fields.Char(string = "Локальный путь")
    description = fields.Char(string = "Описание")
    uploader = fields.Many2one('res.users', string = "Загружен пользователем")
    