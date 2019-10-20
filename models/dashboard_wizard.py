# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DashboardForm(models.Model):
    _name='toonproject.dashboard'
    name = fields.Char()
    _description = 'Singleton model for display user tasks dashboard as a record form with some m2m fields'

    @api.multi
    def _my_tasks(self):
        for rec in self:
            rec.my_tasks =  self.env['toonproject.task'].search([('worker_id','=',self.env.uid),('status','!=','7finished'),('status','!=','1pending'),('status','!=','8canceled'),('status','!=','6control')])

    @api.multi
    def _for_pay(self):
        for rec in self:
            rec.for_pay =  self.env['toonproject.task'].search([('worker_id','=',self.env.uid),('status','=','7finished'),('pay_date','=',None)])

    @api.multi
    def _valid_tasks(self):
        for rec in self:
            ready_tasks =  self.env['toonproject.task'].search([('status','=','2ready')])
            tasks = self.env['toonproject.task']
            for task in ready_tasks:
                if ((not task.valid_group) or self.env.user.id in task.valid_group.users.ids) and (not task.worker_id.id or task.worker_id.id == self.env.uid):
                    tasks |= task
            rec.valid_tasks = tasks

    @api.multi
    def _my_control(self):
        for rec in self:
            control_tasks =  self.env['toonproject.task'].search([('status','=','6control')])
            tasks = self.env['toonproject.task']
            for task in control_tasks:
                if task.isControler:
                    tasks |= task
            rec.my_control = tasks

    my_tasks = fields.Many2many('toonproject.task',
                                 string="В работе", required=True, compute='_my_tasks')

    valid_tasks = fields.Many2many('toonproject.task',
                                 string="Можно взять в работу", required=True, compute='_valid_tasks')

    my_control = fields.Many2many('toonproject.task',
                                 string="Мне в проверку", required=True, compute='_my_control')

    for_pay = fields.Many2many('toonproject.task',
                                 string="В оплату", required=True, compute='_for_pay')

