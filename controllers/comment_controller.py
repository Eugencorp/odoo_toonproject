# -*- coding: utf-8 -*-
from odoo import http
import requests
import datetime


class Toonproject(http.Controller):
    @http.route('/toonproject/comment', auth='user', method=['POST', 'GET'], csrf=False)    
    def comment(self, t, **kw):
        task = http.request.env['toonproject.task'].search([('id', '=', int(str.replace(t,',','')))])
        if not task:
            return http.Response("Не найдено задания с идентификатором " + t, status=200)