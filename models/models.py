# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID
from odoo import tools
from odoo.exceptions import ValidationError

class group(models.Model):
    _name = 'res.groups'
    _inherit = 'res.groups'
    max_tasks = fields.Integer(string="Количество одновременных заданий")

class controler(models.Model):
    _name = 'toonproject.controler'
    _order = 'sequence,name'
    _description = 'Simple model for ordering multiple controlers bent to some project task type'

    user = fields.Many2one('res.users', required=True, ondelete='restrict')
    sequence = fields.Integer(default=10)
    price = fields.Many2one('toonproject.price', required=True, ondelete='cascade')
    name = fields.Char(compute='_get_name', store=True)

    @api.depends('user')
    def _get_name(self):
        for rec in self:
            rec.name = rec.user.display_name


class assettype(models.Model):
    _name = 'toonproject.assettype'
    _description = 'asset category, sets wish task types can be created for an asset'

    name = fields.Char(string="Тип")
    description = fields.Text()
    valid_tasktypes = fields.Many2many('toonproject.tasktype', string = "Возможные виды работ:")

class tasktype(models.Model):
    _name = 'toonproject.tasktype'
    _description = 'task type for wich prices and pipeline are set'

    name = fields.Char(string="Вид работ")
    description = fields.Text()
    valid_assettypes = fields.Many2many('toonproject.assettype', string = "Над чем производятся работы:")

class price(models.Model):
    _name = 'toonproject.price'
    _description = 'some info, such as price, controlers, pipeline and valid worker groups bent to a project and a task type'

    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='set null')
    tasktype_id = fields.Many2one('toonproject.tasktype', string="Вид работ", ondelete='set null')
    value = fields.Float(string="Расценка за единицу")

    # controler_id = fields.Many2one('res.users', string='контроль')
    # precontroler_id = fields.Many2one('res.users', string='предварительный контроль')
    next_tasktype = fields.Many2one('toonproject.tasktype', string='следующий процесс')
    valid_group = fields.Many2one('res.groups', string='группа работников')

    controlers = fields.One2many('toonproject.controler', 'price', string='контроль')

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.tasktype_id.name + ' по проекту ' + rec.project_id.name))
        return res



class cartoon(models.Model):
    _name = 'toonproject.cartoon'
    _description = 'a project, hierarchial structure'

    name = fields.Char()
    description = fields.Text()

    parent_id = fields.Many2one('toonproject.cartoon', string="Родительский проект", ondelete='restrict', index=True)
    child_ids = fields.One2many('toonproject.cartoon', 'parent_id', string='Дочерние проекты')
    _parent_store = True
    _parent_name = "parent_id"
    parent_path = fields.Char(index=True)

    price_ids = fields.One2many('toonproject.price', 'project_id')


    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive projects.')

    @api.multi
    def name_get(self):
        def get_names(cat):
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res
        res = []
        for record in self:
            res.append((record.id, " / ".join(reversed(get_names(record)))))
        return res


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
    _description = 'some meaning part of a production: a scene, a background or a rig'

    name = fields.Char(required=True)
    short_description = fields.Char()
    description = fields.Text()
    factor = fields.Float(default=1)

    size = fields.Float(default=1)
    
    assettype_id = fields.Many2one('toonproject.assettype', string='Тип', default=1, required=True)
    task_ids = fields.Many2many('toonproject.task', string="Задачи")
    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='restrict', required=True)

    color = fields.Integer(compute='_get_type_color', store=True)
    current_status = fields.Selection([('1pending', 'пауза'),('2ready','в работу'),('3progress','в процессе'),('4control','в проверку'),('5finished','готово'),('6canceled', 'отменено')], default='1pending', compute='_get_current_tasktype', store=True)
    current_tasktype = fields.Many2one('toonproject.tasktype', compute='_get_current_tasktype',store=True)
    
    icon_image = fields.Binary(string='Иконка:', attachment=False)
    
    icon_video_url = fields.Char(string='URL иконки:')
    
    icon_video = fields.Binary(compute='_compute_image', store=True, attachment=False)
    
    @api.depends('assettype_id')
    def _get_type_color(self):
        for rec in self:
            if rec.assettype_id:
                rec.color = rec.assettype_id.id
            else:
                rec.color = 0

    @api.depends('task_ids')
    def _get_current_statuses(self):
        for rec in self:
            task_states = []
            for task in rec.task_ids:
                for valid_tasktype in rec.assettype_id.valid_tasktypes:
                    if valid_tasktype == task.tasktype_id:
                        task_states.append(task.status)
                        break
            task_states.sort()


    @api.depends('task_ids')
    def _get_current_tasktype(self):
        for rec in self:
            task_types = []
            for task in rec.task_ids:
                for valid_tasktype in rec.assettype_id.valid_tasktypes:
                    if valid_tasktype == task.tasktype_id and task.status > '1pending':
                        task_types.append(task)
                        break
            if len(task_types):
                task_types.sort(key=lambda task: task.status)
                rec.current_tasktype = task_types[0].tasktype_id
                rec.current_status = task_types[0].status
            else:
                rec.current_status = '1pending'

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
    _description = 'main model for work'

    name = fields.Char()
    tasktype_id = fields.Many2one('toonproject.tasktype',  ondelete='restrict', index=True, required=True)
    factor = fields.Float(default=1)
    short_description = fields.Char()
    description = fields.Text()
    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='restrict', required=True)
    
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
    isManager = fields.Boolean(compute='_is_manager', store=False, default=True)

    color = fields.Integer(compute='_raw_tasktype', store=True)

    def _is_manager(self):
        for rec in self:
            if self.id == 0 or self.env.user.has_group('toonproject.group_toonproject_manager') or self.env.user.has_group('toonproject.group_toonproject_admin') or self.env.user.id == SUPERUSER_ID:
                rec.isManager = True
            else:
                rec.isManager = False

    @api.multi
    def _default_control(self):
        for rec in self:
            controlers = self.env['toonproject.controler'].search([('price', '=', rec.price_record.id)], order='sequence asc', limit=1)
            if len(controlers) > 0:
                rec.current_control = controlers[0].id

    @api.onchange('price_record')
    def update_current_control(self):
        controlers = self.env['toonproject.controler'].search([('price', '=', self.price_record.id)],
                                                              order='sequence asc', limit=1)
        if len(controlers) > 0:
            self.current_control = controlers[0].id

    price_record = fields.Many2one('toonproject.price', compute='_get_price_record',store=False)
    current_control = fields.Many2one('toonproject.controler', string="должен проверить", default=_default_control, track_visibility='onchange')
    controler_names = fields.Char(compute='_get_controler_names', store=False, string="контролеры")

    @api.depends('price_record','tasktype_id','project_id')
    def _get_controler_names(self):
        for rec in self:
            if rec.price_record and rec.price_record.controlers:
                controlers = self.env['toonproject.controler'].search([('price', '=', rec.price_record.id)],order='sequence asc')
                res = ''
                for controler in controlers:
                    res = res + controler.name + ', '
                if len(controlers):
                    res = res[:-2]
                rec.controler_names = res

    @api.depends('tasktype_id')
    def _raw_tasktype(self):
        for rec in self:
            if rec.tasktype_id:
                rec.color = rec.tasktype_id.id
            else:
                rec.color = 0

    @api.depends('current_control')
    def _is_controler(self):
        for rec in self:
            if not rec.current_control:
                rec.isControler = False
            else:
                rec.isControler = (self.env.user.id == rec.current_control.user.id)

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

    def findPriceInProject(self):
        project = self.project_id
        while len(project)>0:
            for price in project.price_ids:
                if price.tasktype_id == self.tasktype_id:
                    return price
            project = project.parent_id


    @api.depends('project_id','tasktype_id')
    def _get_price_record(self):
        for rec in self:
            rec.price_record = rec.findPriceInProject()


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
        ctx = {'btn': True}
        for rec in self:
            rec.with_context(ctx).write({
                'status': '3progress',
                'work_start': fields.Date.today(),
                'worker_id': rec.worker_id.id|self.env.user.id
            })
    @api.multi
    def button_control(self):
        ctx = {'btn': True}
        for rec in self:
            rec.with_context(ctx).write({'status': '4control'})

    @api.multi
    def button_reject(self):
        ctx = {'btn': True}
        for rec in self:
            rec.with_context(ctx).write({'status': '3progress'})

    @api.multi
    def button_accept(self):
        ctx = {'btn': True}
        for rec in self:
            controlers = self.env['toonproject.controler'].search([
                ('price', '=', rec.price_record.id),
                ('sequence', '>', rec.current_control.sequence)],
                order='sequence asc')
            if len(controlers)<1:
                rec.with_context(ctx).write({
                    'status': '5finished',
                    'real_finish': fields.Date.today()
                })
            else:
                rec.with_context(ctx).write({'current_control':controlers[0].id})


    @api.multi
    def write(self, values):
        if (not self.env.context.get('btn')) and \
                self.env.user.id != SUPERUSER_ID and \
                not self.env.user.has_group('toonproject.group_toonproject_manager'):
            readonly_fields = ['name', 'project_id',
                               'description', 'short_description',
                               'factor','compute_price_method',
                               'asset_ids', 'affecting_tasks','dependent_tasks',
                               'valid_group', 'current_control',
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
        return super(task, self).write(values)

    def open_task_view_py(self):
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
                            'project_id': asset.project_id.id
                        }
                    )
            for task in created:
                priceRec = task.price_record
                if priceRec:
                    next_type = priceRec.next_tasktype
                    for next_task in created:
                        if next_task.tasktype_id == next_type:
                            task.dependent_tasks |= next_task
                            break
                    task.valid_group = priceRec.valid_group
                    task._default_control()


        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'toonproject.task',
            'view_type': 'form',
            'view_mode': 'tree,form',
        }

class EditTasksWizard(models.TransientModel):
    _name = 'toonproject.edittasks_wizard'
    _description = "Wizard: Edit multiple tasks at once"

    def _default_valid_group(self):
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))
        for rec in target_recs:
            if rec.valid_group:
                return rec.valid_group

    valid_group = fields.Many2one('res.groups', string="Группа исполнителей", default=_default_valid_group)
    worker_id = fields.Many2one('res.user', string="Исполнитель")
    factor = fields.Float(default=1, string="Cложность")
    status = fields.Selection(
        [('1pending', 'пауза'), ('2ready', 'в работу'), ('3progress', 'в процессе'), ('4control', 'в проверку'),
         ('5finished', 'готово'), ('6canceled', 'отменено')], string='Статус', default='1pending',
        )

    valid_group_chk = fields.Boolean(default=False)
    worker_id_chk = fields.Boolean(default=False)
    factor_chk = fields.Boolean(default=False)
    status_chk = fields.Boolean(default=False)

    @api.multi
    def apply_tasks(self):
        values = {}
        if self.valid_group_chk:
            values.update({'valid_group': self.valid_group.id})
        if self.worker_id_chk:
            values.update({'worker_id': self.worker_id.id})
        if self.factor_chk:
            values.update({'factor': self.factor})
        if self.status_chk:
            values.update({'status': self.status})
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))
        for rec in target_recs:
            rec.write(values)
        return {}

class CombineTasksWizard(models.TransientModel):
    _name = 'toonproject.combinetasks_wizard'
    _description = "Wizard: Combine multiple tasks"
    _inherit = 'toonproject.task'

    def _is_valid_operation(self):

        return True

    valid_operation = fields.Boolean(default=_is_valid_operation)
    delete_or_archive = fields.Selection([('archive', 'архивировать'), ('delete', 'убить')])

    @api.multi
    def combine_tasks(self):
        return{}