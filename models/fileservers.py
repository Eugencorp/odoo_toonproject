# -*- coding: utf-8 -*-

from odoo import models, fields, api

class upload_interface(models.Model):
    _name = 'toonproject.upload_interface'
    _description = 'Simple model for storing paths to file upload controlers'
    
    name = fields.Char()
    path = fields.Char()
    
class fileserver_setting(models.Model):
    _name = 'toonproject.fileserver_setting'
    _description = 'Simple model for storing login, password and other settings for uploading files to a server'
    
    name = fields.Char(string="Условное название для настроек вашего сервера")
    controler = fields.Many2one('toonproject.upload_interface', string="Обработчик загрузок", default=None)
    controler_path = fields.Char(compute = '_get_controler_path')
    
    login = fields.Char(string="login")
    password = fields.Char(string="password")
    upload_root = fields.Char(string="Куда загружать")
    external_root = fields.Char(string="Внешний доступ через http")
    
    @api.depends('controler')    
    def _get_controler_path(self):
        for rec in self:
            if rec.controler:
                rec.controler_path = rec.controler.path
            else:
                rec.controler_path = ''