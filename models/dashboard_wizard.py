# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DashboardForm(models.Model):
    _name='toonproject.dashboard'
    name = fields.Char()

    @api.multi
    def _my_tasks(self):
        for rec in self:
            rec.my_tasks =  self.env['toonproject.task'].search([('worker_id','=',self.env.uid)])

    @api.multi
    def _valid_tasks(self):
        for rec in self:
            ready_tasks =  self.env['toonproject.task'].search([('status','=','ready')])
            tasks = self.env['toonproject.task']
            for task in ready_tasks:
                if (not task.valid_group) or self.env.user.id in task.valid_group.users.ids:
                    tasks |= task
            rec.valid_tasks = tasks

    my_tasks = fields.Many2many('toonproject.task',
                                 string="В работе", required=True, compute='_my_tasks')

    valid_tasks = fields.Many2many('toonproject.task',
                                 string="Можно взять в работу", required=True, compute='_valid_tasks')

class DashboardWizard(models.TransientModel):
    _name = 'toonproject.dashboard_wizard'

    def _my_tasks(self):
        return self.env['toonproject.task'].search([])

    my_tasks = fields.Many2many('toonproject.task',
                                 string="В работе", required=True, default=_my_tasks)