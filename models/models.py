# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
    size = fields.Float(default=1)
    
    assettype_id = fields.Many2one('toonproject.assettype', string='Тип', default=0)
    task_ids = fields.Many2many('toonproject.task', string="Задачи")
    project_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='set null')
    
    icon_image = fields.Binary(string='Иконка:', attachment=False)
    
    icon_video_url = fields.Char(string='URL иконки:')
    
    icon_video = fields.Binary(compute='_compute_image', store=True, attachment=False)

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
    

class task(models.Model):
    _name = 'toonproject.task'
    _inherit = 'mail.thread'
    
    name = fields.Char()
    #type = fields.Selection([('anim','мультипиликат'),('lo','лэй-аут'),('compose','композ'),('rig','риг'),('draw','графика'),('paint','живопись')],'Тип работ', default='anim')
    tasktype_id = fields.Many2one('toonproject.tasktype',  ondelete='set null', index=True)
    factor = fields.Float(default=1)    
    description = fields.Text()
    
    controler_id = fields.Many2one('res.users', ondelete='set null', index=True)
    worker_id = fields.Many2one('res.users', ondelete='set null', index=True)
    work_start = fields.Date()
    plan_finish = fields.Date()
    real_finish = fields.Date()
    
    asset_ids = fields.Many2many('toonproject.asset', string="Материалы")
    compute_price_method = fields.Selection([('first','по первому допустимому'),('sum', 'по сумме допустимых')], default = 'first', string = 'Метод рассчета')
    computed_price = fields.Float(compute='_compute_price')
    
    @api.depends('asset_ids', 'compute_price_method', 'factor', 'tasktype_id')
    def _compute_price(self):
        for record in self:
            sum = 0
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
                sum = sum + foundprice * record.factor * asset.size
                if record.compute_price_method == 'first':
                    break                
            record.computed_price = sum
    
    # last_status (calculate?)

    