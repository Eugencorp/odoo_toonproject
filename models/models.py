# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID
from odoo import tools

class assettype(models.Model):
    _name = 'toonproject.assettype'
    
    name = fields.Char(string="Тип")
    description = fields.Text()
    valid_tasktypes = fields.Many2many('toonproject.tasktype', string = "Возможные виды работ:")

class tasktype(models.Model):
    _name = 'toonproject.tasktype'
    
    name = fields.Char(string="Вид работ")
    description = fields.Text()
    valid_assettypes = fields.Many2many('toonproject.assettype', string = "Над чем производятся работы:")    
    
class price(models.Model):
    _name = 'toonproject.price'
    
    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='set null')
    tasktype_id = fields.Many2one('toonproject.tasktype', string="Вид работ", ondelete='set null')
    value = fields.Float(string="Расценка за единицу")

    controler_id = fields.Many2one('res.users', string='контроль')
    precontroler_id = fields.Many2one('res.users', string='предварительный контроль')
    next_tasktype = fields.Many2one('toonproject.tasktype', string='следующий процесс')
    valid_group = fields.Many2one('res.groups', string='группа работников')
    

class cartoon(models.Model):
    _name = 'toonproject.cartoon'
    
    name = fields.Char()
    description = fields.Text()
    
    parent_id = fields.Many2one('toonproject.cartoon', string="Родительский проект", ondelete='set null')
    price_ids = fields.One2many('toonproject.price', 'project_id')
    

import requests, logging, base64
_logger = logging.getLogger(__name__)

class StoresImages():
    """
    Image mixin for odoo.models.Model to utilize if the data model deals with
    storing Binary fields or images.
    """

    def fetch_image_from_url(self, url):
        """
        Gets an image from a URL and converts it to an Odoo friendly format
        so that we can store it in a Binary field.
        :param url: The URL to fetch.
        :return: Returns a base64 encoded string.
        """
        data = ''

        try:
            # Python 2
            # data = requests.get(url.strip()).content.encode('base64').replace('\n', '')

            # Python 3

            data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
        except Exception as e:
            _logger.warn('There was a problem requesting the image from URL %s' % url)
            logging.exception(e)

        return data


class asset(models.Model, StoresImages):
    _name = 'toonproject.asset'

    name = fields.Char()
    short_description = fields.Char()
    description = fields.Text()
    factor = fields.Float(default=1)

    size = fields.Float(default=1)
    
    assettype_id = fields.Many2one('toonproject.assettype', string='Тип', default=0)
    task_ids = fields.Many2many('toonproject.task', string="Задачи")
    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='set null')
    
    icon_image = fields.Binary(string='Иконка:', attachment=False)
    
    icon_video_url = fields.Char(string='URL иконки:')
    
    icon_video = fields.Binary(compute='_compute_image', store=True, attachment=False)
    
    '''
    def create_multiple_tasks(self, cursor, uid, ids, tasktype_ids, context):
        n = 0 #temporal placeholder
        for id in ids:
            n = n + 1 #temporal placeholder
        return True
    '''

    @api.multi
    @api.depends('icon_video_url')
    def _compute_image(self):
        """
        Computes the image Binary from the `image_url` per database record
        automatically.
        
        :return: Returns NoneType
        """
        for record in self:
            image = None
            if record.icon_video_url:
                image = self.fetch_image_from_url(record.icon_video_url)
            record.update({'icon_video': image, })

    @api.multi
    def write(self, values):
        if values.get('icon_image'):
            tools.image_resize_images(values, big_name='icon_image', sizes={'icon_image': (256, 144)})
        return super().write(values)

    def name_get(self,context=None):
        res = []
        for record in self:
            complex_name = record.assettype_id.name + ' ' + record.name
            res.append((record.id, complex_name))
        return res

class task(models.Model):
    _name = 'toonproject.task'
    _inherit = 'mail.thread'

    name = fields.Char()
    tasktype_id = fields.Many2one('toonproject.tasktype',  ondelete='set null', index=True)
    factor = fields.Float(default=1)
    short_description = fields.Char()
    description = fields.Text()
    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='set null', required=True)
    
    controler_id = fields.Many2one('res.users', ondelete='set null', index=True)
    precontroler_id = fields.Many2one('res.users', ondelete='set null', index=True)
    worker_id = fields.Many2one('res.users', ondelete='set null', index=True)
    work_start = fields.Date()
    plan_finish = fields.Date()
    real_finish = fields.Date()
    
    asset_ids = fields.Many2many('toonproject.asset', string="Материалы")
    compute_price_method = fields.Selection([('first','по первому допустимому'),('sum', 'по сумме допустимых')], default = 'first', string = 'Метод рассчета')
    computed_price = fields.Float(compute='_compute_price')
    pay_date = fields.Date()
    
    status = fields.Selection([('1pending', 'пауза'),('2ready','в работу'),('3progress','в процессе'),('4control','в проверку'),('5finished','готово'),('6canceled', 'отменено')], string='Статус', default='1pending', track_visibility='onchange')
    dependent_tasks = fields.Many2many('toonproject.task', 'task2task', 'source', 'target', string='зависимые задачи')
    affecting_tasks = fields.Many2many('toonproject.task', 'task2task', 'target', 'source', string='влияющие задачи')
    valid_group = fields.Many2one('res.groups', string='группа работников')

    isControler = fields.Boolean(compute='_is_controler', store=False)
    isWorker = fields.Boolean(compute='_is_worker', store=False)
    isValidWorker = fields.Boolean(compute='_is_valid_worker', store=False)
    isManager = fields.Boolean(compute='_is_manager', store=False)

    color = fields.Integer()

    def _is_manager(self):
        for rec in self:
            if self.env.user.has_group('toonproject.group_toonproject_manager') or self.env.user.id == SUPERUSER_ID:
                rec.isManager = True
            else:
                rec.isManager = False


    @api.multi
    def _default_control(self):
        for rec in self:
            if rec.precontroler_id:
                rec.current_control = rec.precontroler_id
            else:
                rec.current_control = rec.controler_id

    current_control = fields.Many2one('res.users', string="должен проверить", default=_default_control, track_visibility='onchange')

    @api.depends('current_control')
    def _is_controler(self):
        for rec in self:
            if not rec.current_control:
                rec._default_control()
            rec.isControler = (self.env.user.id == rec.current_control.id)
    @api.depends('worker_id')
    def _is_worker(self):
        for rec in self:
            rec.isWorker = (self.env.user.id == rec.worker_id.id)

    @api.depends('worker_id','valid_group')
    def _is_valid_worker(self):
        for rec in self:
            rec.isValidWorker = (self.env.user.id == rec.worker_id.id)
            if not rec.worker_id.id:
                rec.isValidWorker = (not rec.valid_group) or (self.env.user.id in rec.valid_group.users.ids)

    def getMainAsset(self):
        #find first asset have legal tasktype
        for asset in self.asset_ids:
            for valid_tasktype in asset.assettype_id.valid_tasktypes:
                if valid_tasktype == self.tasktype_id:
                    return asset
        return None

    def getProject(self):
        if self.project_id:
            return self.project_id
        gotMainAsset = self.getMainAsset()
        if gotMainAsset:
            return gotMainAsset.project_id
        return None

    def getPriceRecord(taskRec, assetRec):
        '''
        if not assetRec:
            assetRec = taskRec.getMainAsset()
        if not assetRec:
            return None
        project = assetRec.project_id
        '''

        project = taskRec.project_id
        type = taskRec.tasktype_id

        while project:
            for price in project.price_ids:
                if price.tasktype_id == type:
                    return price
            project = project.parent_id


    @api.depends('asset_ids', 'compute_price_method', 'factor', 'tasktype_id')
    def _compute_price(self):
        for record in self:
            sm = 0
            for asset in record.asset_ids:
                assettype = asset.assettype_id
                is_valid = False
                for validtype in assettype.valid_tasktypes:
                    if validtype == record.tasktype_id:
                        is_valid = True
                        break
                if not is_valid:
                    continue                    
                project = asset.project_id
                foundprice = 0
                while project:
                    for price in project.price_ids:
                        if price.tasktype_id == record.tasktype_id:
                            foundprice = price.value
                            break
                    project = project.parent_id     
                sm = sm + foundprice * record.factor * asset.size
                if record.compute_price_method == 'first':
                    break                
            record.computed_price = sm
    
    @api.multi
    def button_start(self):
        for rec in self:
            rec.sudo().write({
                'status': '3progress',
                'work_start': fields.Date.today(),
                'worker_id': rec.worker_id.id|self.env.user.id
            })
    @api.multi
    def button_control(self):
        for rec in self:
            rec.sudo().write({'status': '4control'})

    @api.multi
    def button_reject(self):
        #import pdb
        #pdb.set_trace()
        for rec in self:
            if rec.precontroler_id and rec.current_control.id == rec.controler_id.id:
                rec.sudo().write({'current_control': rec.precontroler_id.id})
            rec.sudo().write({'status': '3progress'})

    @api.multi
    def button_accept(self):
        for rec in self:
            if rec.current_control.id == rec.controler_id.id:
                rec.sudo().write({
                    'status': '5finished',
                    'real_finish': fields.Date.today()
                })
            else:
                rec.sudo().write({'current_control':rec.controler_id.id})


    @api.multi
    def write(self, values):
        if self.env.user.id != SUPERUSER_ID and not self.env.user.has_group('toonproject.group_toonproject_manager'):
            readonly_fields = ['name', 'description', 'short_description',
                               'factor','compute_price_method',
                               'asset_ids', 'affecting_tasks','dependent_tasks',
                               'controler_id', 'precontroler_id', 'valid_group',
                               'worker_id','work_start','real_finish',
                               'status']
            for ro_field in readonly_fields:
                if values.get(ro_field):
                    raise UserError(
                        'У вас нет прав на это действие'
                    )
        if values.get('status') == '5finished':
            for rec in self:
                for dependent_task in rec.dependent_tasks:
                    if dependent_task.status == '1pending':
                        to_begin = True
                        for affecting_task in dependent_task.affecting_tasks:
                            if affecting_task!=self and affecting_task.status != '5finished' and affecting_task!='6canceled':
                                to_begin = False
                                break
                        if to_begin:
                            dependent_task.status = "2ready"
        if values.get('controler_id') or values.get('precontroler_id'):
            for rec in self:
                rec.current_control = values.get('precontroler_id') or values.get('controler_id')
        return super(task, self).write(values)

    def open_task_view_py(self):
        #import pdb
        #pdb.set_trace()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'toonproject.task',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }


class CreateTasksWizard(models.TransientModel):
    _name = 'toonproject.createtasks_wizard'
    _description = "Wizard: Create tasks for selected assets"

    def _default_assets(self):
        return self.env['toonproject.asset'].browse(self._context.get('active_ids'))

    asset_ids = fields.Many2many('toonproject.asset',
        string="Материалы", required=True, default=_default_assets)
    tasktype_ids = fields.Many2many('toonproject.tasktype', string="Типы задач")
    
    @api.multi
    def create_tasks(self):
        for asset in self.asset_ids:
            created = self.env['toonproject.task']
            for tasktype in self.tasktype_ids:
                tasktype_is_valid = False
                for valid_assettype in tasktype.valid_assettypes:
                    if valid_assettype == asset.assettype_id:
                        tasktype_is_valid = True
                        break
                if tasktype_is_valid:
                    name = tasktype.name + " " + asset.name 
                    created = created|self.env['toonproject.task'].create(
                        {
                            'name': name,
                            'tasktype_id': tasktype.id,
                            'asset_ids': [(4,asset.id)],
                            'short_description': asset.short_description,
                            'description': asset.description,
                            'factor': asset.factor,
                            'project_id': asset.project_id
                        }
                    )
            for task in created:
                priceRec = task.getPriceRecord(asset)
                if priceRec:
                    next_type = priceRec.next_tasktype
                    for next_task in created:
                        if next_task.tasktype_id == next_type:
                            task.dependent_tasks |= next_task
                            break
                    task.valid_group = priceRec.valid_group
                    task.controler_id = priceRec.controler_id
                    task.precontroler_id = priceRec.precontroler_id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'toonproject.task',
            'view_type': 'form',
            'view_mode': 'tree,form',
        }



