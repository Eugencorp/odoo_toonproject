# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DashboardForm(models.Model):
    _name='toonproject.dashboard'
    name = fields.Char()

    @api.multi
    def _my_tasks(self):
        for rec in self:
            rec.my_tasks =  self.env['toonproject.task'].search([('worker_id','=',self.env.uid),('status','!=','finished'),('status','!=','pause'),('status','!=','canceled')])

    @api.multi
    def _for_pay(self):
        for rec in self:
            rec.for_pay =  self.env['toonproject.task'].search([('worker_id','=',self.env.uid),('status','=','finished'),('pay_date','=',None)])

    @api.multi
    def _valid_tasks(self):
        for rec in self:
            ready_tasks =  self.env['toonproject.task'].search([('status','=','ready')])
            tasks = self.env['toonproject.task']
            for task in ready_tasks:
                if (not task.valid_group) or self.env.user.id in task.valid_group.users.ids:
                    tasks |= task
            rec.valid_tasks = tasks

    @api.multi
    def _my_control(self):
        for rec in self:
            control_tasks =  self.env['toonproject.task'].search([('status','=','control')])
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

