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
    description = fields.Text(string="Описание")
    valid_tasktypes = fields.Many2many('toonproject.tasktype', string = "Возможные виды работ:")
    
    valid_measures = fields.Many2many('toonproject.measures', required = True, string = "Возможные единицы измерения:")

    active_measure = fields.Many2one('toonproject.measures', string="В чем измерять", compute="_get_measure_unit", store=False)
    
    def _get_measure_unit(self):
        for rec in self:
            if len(rec.valid_measures)<1:
                rec.active_measure = self.env['toonproject.measures'].search([])[0]
            elif len(rec.valid_measures)<2:
                rec.active_measure = rec.valid_measures[0]
            else:
                settings = self.env['toonproject.measure_setting'].search([('user','=',self.env.user.id),('asset_type','=',rec.id)])
                if len(settings) > 0:
                    rec.active_measure = settings[0].measure
                else:
                    rec.active_measure = rec.valid_measures[0]  


class tasktype(models.Model):
    _name = 'toonproject.tasktype'
    _description = 'task type for wich prices and pipeline are set'
    _order = "sequence,id"

    name = fields.Char(string="Вид работ")    
    sequence = fields.Integer(default=10)
    description = fields.Text()
    valid_assettypes = fields.Many2many('toonproject.assettype', string = "Над чем производятся работы:")

class price(models.Model):
    _name = 'toonproject.price'
    _description = 'some info, such as price, controlers, pipeline and valid worker groups bent to a project and a task type'
    _order = 'sequence,id'

    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='set null')
    tasktype_id = fields.Many2one('toonproject.tasktype', string="Вид работ", ondelete='set null')
    value = fields.Float(string="Расценка за единицу")

    #next_tasktype = fields.Many2one('toonproject.tasktype', string='следующий процесс')
    valid_group = fields.Many2one('res.groups', string='группа работников')

    controlers = fields.One2many('toonproject.controler', 'price', string='контроль')
    
    def _default_sequence(self):
            prices=self.env['toonproject.price'].search([],order="sequence desc",limit=1)
            return len(prices)>0 and (prices[0].sequence+1) or 10
    
    sequence = fields.Integer(default=_default_sequence)

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

    name = fields.Char(required=True,string="Название")
    short_description = fields.Char(string="Краткое содержание")
    description = fields.Text(string="Описание")
    factor = fields.Float(default=1,string="Ориентировочная сложность")

    size = fields.Float(default=1,string="Размер")
    size_unit = fields.Many2many('toonproject.measures', compute="_get_size_unit", store=False)
    size_unit_naming = fields.Char(compute="_get_size_unit_naming", store=False)
    size_precision = fields.Char(compute="_get_size_precision", store=False)
    
    assettype_id = fields.Many2one('toonproject.assettype', string='Тип', default=1, required=True)
    task_ids = fields.Many2many('toonproject.task', string="Задачи")
    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='restrict', required=True)

    color = fields.Integer(compute='_get_type_color', store=True)
    current_status = fields.Selection([('1pending', 'пауза'),('2ready','в работу'),('3progress','в процессе'),('4torevision', 'в поправки'),('5inrevision','в поправках'),('6control','в проверку'),('7finished','готово'),('8canceled', 'отменено')], default='1pending', compute='_get_current_tasktype', store=True)
    current_tasktype = fields.Many2one('toonproject.tasktype', compute='_get_current_tasktype',store=True)
    
    icon_image = fields.Binary(string='Иконка:', attachment=False)
    
    icon_video_url = fields.Char(string='URL иконки:')
    
    icon_video = fields.Binary(compute='_compute_image', store=True, attachment=False)
    
    def _get_size_unit(self):
        for rec in self:
            rec.size_unit = rec.assettype_id.active_measure
            
    def _get_size_unit_naming(self):
        for rec in self:
            rec.size_unit_naming = rec.assettype_id.active_measure.unit_naming   

    def _get_size_precision(self):
        for rec in self:
            rec.size_precision = rec.assettype_id.active_measure.precision 

   
    @api.depends('assettype_id')
    def _get_type_color(self):
        for rec in self:
            if rec.current_status:
                rec.color = int(rec.current_status[:1])
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
                    if valid_tasktype == task.tasktype_id:
                        pseudo_task = {'tasktype_id':task.tasktype_id, 'status':task.status}
                        if self.env.context.get('task') and self.env.context.get('task')==task.id:
                            pseudo_task.update({'status':self.env.context.get('status')})
                        if pseudo_task['status'] > '1pending':
                            task_types.append(pseudo_task)
                            break
            if len(task_types):
                task_types.sort(key=lambda task: task['status'])
                rec.current_tasktype = task_types[0]['tasktype_id']
                rec.current_status = task_types[0]['status']
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

    name = fields.Char(string='Название')
    tasktype_id = fields.Many2one('toonproject.tasktype',  ondelete='restrict', index=True, required=True, string='Вид работ')
    factor = fields.Float(default=1, string='Сложность')
    short_description = fields.Char(string='Краткое содержание')
    description = fields.Text(string='Описание задачи')
    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='restrict', required=True)
    
    worker_id = fields.Many2one('res.users', ondelete='set null', index=True, string='Исполнитель')
    work_start = fields.Date(string='Начато')
    plan_finish = fields.Date(string='Планируется закончить')
    real_finish = fields.Date(string='Закончено')
    
    asset_ids = fields.Many2many('toonproject.asset', string="Материалы")

    compute_price_method = fields.Selection([('first','по первому из материалов'),('sum', 'по сумме соизмеримых материалов')], default = 'sum', string = 'Метод рассчета')
    computed_price = fields.Float(compute='_compute_price',string='Стоимость')
    pay_date = fields.Date(string='Оплачено')
    asset_names = fields.Char(string="Названия материалов", compute="_get_asset_names", store=True)

    
    status = fields.Selection([('1pending', 'пауза'),('2ready','в работу'),('3progress','в процессе'),('4torevision', 'в поправки'),('5inrevision', 'в поправках'),('6control','в проверку'),('7finished','готово'),('8canceled', 'отменено')], string='Статус', default='1pending', track_visibility='onchange')
    dependent_tasks = fields.Many2many('toonproject.task', 'task2task', 'source', 'target', string='зависимые задачи')
    affecting_tasks = fields.Many2many('toonproject.task', 'task2task', 'target', 'source', string='зависит от')
    valid_group = fields.Many2one('res.groups', string='Кому можно выдавать')

    isControler = fields.Boolean(compute='_is_controler', store=False)
    isWorker = fields.Boolean(compute='_is_worker', store=False)
    isValidWorker = fields.Boolean(compute='_is_valid_worker', store=False)
    isManager = fields.Boolean(compute='_is_manager', store=False, default=True)

    color = fields.Integer(compute='_raw_tasktype', store=True)
    
    @api.depends('asset_ids')
    def _get_asset_names(self):
        for rec in self:
            names = ", ".join([asset.name for asset in rec.asset_ids])
            rec.asset_names = names
        

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
            new_state = '3progress'
            if rec.status == '4torevision':
                new_state = '5inrevision'
            rec.with_context(ctx).write({
                'status': new_state,
                'work_start': fields.Date.today(),
                'worker_id': rec.worker_id.id|self.env.user.id
            })
    @api.multi
    def button_control(self):
        ctx = {'btn': True}
        for rec in self:
            rec.with_context(ctx).write({'status': '6control'})

    @api.multi
    def button_reject(self):
        ctx = {'btn': True}
        for rec in self:
            rec.with_context(ctx).write({'status': '4torevision'})

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
                    'status': '7finished',
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
        if values.get('status'):
            for rec in self:
                for asset in rec.asset_ids:
                    ctx = {'task':rec.id, 'status': values.get('status')}
                    asset.with_context(ctx)._get_current_tasktype()
        if values.get('status') == '7finished':
            for rec in self:
                for dependent_task in rec.dependent_tasks:
                    if dependent_task.status == '1pending':
                        to_begin = True
                        for affecting_task in dependent_task.affecting_tasks:
                            if affecting_task!=self and affecting_task.status != '7finished' and affecting_task!='8canceled':
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
                    next_records = self.env['toonproject.price'].search([('project_id','=',priceRec.project_id.id), ('sequence', '>', priceRec.sequence)], order='sequence asc')
                    next_record = None
                    for price in next_records:
                        if price.tasktype_id in asset.assettype_id.valid_tasktypes:
                            next_record = price
                            break
                    if next_record:
                        for next_task in created:
                            if next_task.price_record and next_task.price_record == next_record[0]:
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
    worker_id = fields.Many2one('res.users', string="Исполнитель")
    factor = fields.Float(default=1, string="Cложность")
    status = fields.Selection(
        [('1pending', 'пауза'), ('2ready', 'в работу'), ('3progress', 'в процессе'), ('4torevision', 'в поправки'),
        ('5inrevision', 'в поправках'),('6control','в проверку'),('7finished','готово'),('8canceled', 'отменено')], string='Статус', default='1pending',
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
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))
        if len(target_recs)<2:
            return "Не выбраны задания для объединения"
        common_tasktype = target_recs[0].tasktype_id
        common_project = target_recs[0].project_id
        for rec in target_recs:
            if rec.worker_id and rec.status > '2ready':
                return "Нельзя объединить задания, уже отданные в работу"
            if rec.tasktype_id!=common_tasktype:
                return "Нельзя объединить задания разного типа"
            if rec.project_id!=common_project:
                return "Нельзя объединить задания из разных проектов"
        return False
           
    def _get_tasktype(self):
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))
        if len(target_recs)>0:
            return target_recs[0].tasktype_id
        else:
            return False
            
    def _get_project(self):
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))
        if len(target_recs)>0:
            return target_recs[0].project_id
        else:
            return False            
        
    def _get_common_short_description(self):
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))
        common_short_description = "; ".join([task.short_description for task in target_recs if task.short_description])
        return common_short_description
        
    def _get_common_description(self):
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))
        common_description = "; ".join([task.description for task in target_recs if task.description])
        return common_description  

    def _get_assets(self):
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))        
        common_assets = self.env['toonproject.asset']
        for rec in target_recs:
            common_assets |= rec.asset_ids
        return common_assets
        
    def _get_factor(self):
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids')) 
        the_price = 0
        the_size = 0
        for rec in target_recs:
            the_price += rec.computed_price
            if rec.factor:
                the_size += rec.computed_price/rec.factor
            else:
                next_size = 0
                for asset in rec.asset_ids:
                    if asset.assettype_id in rec.tasktype_id.valid_assettypes:
                        next_size += asset.size
                the_size += next_size*rec.price_record.value
        return the_price/the_size
        
    
    def _get_dependent_tasks(self):
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))
        res = self.env['toonproject.task']
        for rec in target_recs:
            res |= rec.dependent_tasks
        res = res - target_recs
        return res
        
    
    def _get_affecting_tasks(self):
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))        
        res = self.env['toonproject.task']
        for rec in target_recs:
            res |= rec.affecting_tasks
        res = res - target_recs
        return res    
        


    invalid_message = fields.Char(default=_is_valid_operation)


    delete_or_archive = fields.Selection([('archive', 'архивировать'), ('delete', 'убить')], default='archive', required=True, string='Куда деть старые задачи?')
    
    short_description = fields.Char(default = _get_common_short_description)
    description = fields.Text(default = _get_common_description)
    asset_ids = fields.Many2many('toonproject.asset', default = _get_assets)
    tasktype_id = fields.Many2one('toonproject.tasktype', default = _get_tasktype)
    project_id = fields.Many2one('toonproject.cartoon', default = _get_project)  
    factor = fields.Float(default = _get_factor, string='Сложность')
    dependent_tasks = fields.Many2many('toonproject.task', 'task2task_temporal', 'source', 'target', default=_get_dependent_tasks)    
    affecting_tasks = fields.Many2many('toonproject.task', 'task2task_temporal', 'target', 'source', default=_get_affecting_tasks)
    name = fields.Char(required=True)


    @api.multi
    def combine_tasks(self):
        self.env['toonproject.task'].create({
            'name': self.name,
            'project_id': self.project_id.id,
            'tasktype_id': self.tasktype_id.id,
            'short_description': self.short_description,
            'description': self.description,
            'factor': self.factor,
            'asset_ids': [(6, 0, [asset.id for asset in self.asset_ids])],
            'dependent_tasks': [(6, 0, [task.id for task in self.dependent_tasks])],
            'affecting_tasks': [(6, 0, [task.id for task in self.affecting_tasks])],
            'compute_price_method': self.compute_price_method,
            'worker_id': self.worker_id and self.worker_id.id or False,
            'current_control': self.current_control and self.current_control.id or False,
            'plan_finish': self.plan_finish,
            'valid_group': self.valid_group and self.valid_group.id or False,            
        })
        target_recs = self.env['toonproject.task'].browse(self._context.get('active_ids'))
        if self.delete_or_archive == "archive":
            for task in target_recs:
                task.status = "6canceled"
        elif self.delete_or_archive == "delete":
            target_recs.unlink()
        return{}