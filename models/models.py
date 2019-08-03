# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class toonproject(models.Model):
#     _name = 'toonproject.toonproject'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class cartoon(models.Model):
    _name = 'toonproject.cartoon'
    
    name = fields.Char()
    description = fields.Text()
    
    parent_id = fields.Many2one('toonproject.cartoon', string="Родительский проект", ondelete='set null')


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
    
    type = fields.Selection([('scene','сцена'),('bg','фон'),('rig','риг'),],'Тип', default='scene')
    task_ids = fields.Many2many('toonproject.task', string="Задачи")
    parent_id = fields.Many2one('toonproject.cartoon', string="Проект", ondelete='set null')
    
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
    type = fields.Selection([('anim','мультипиликат'),('lo','лэй-аут'),('compose','композ'),('rig','риг'),('draw','графика'),('paint','живопись')],'Тип работ', default='anim')
    factor = fields.Float(default=1)    
    description = fields.Text()
    
    controler_id = fields.Many2one('res.users', ondelete='set null', index=True)
    worker_id = fields.Many2one('res.users', ondelete='set null', index=True)
    work_start = fields.Date()
    plan_finish = fields.Date()
    real_finish = fields.Date()
    
    asset_ids = fields.Many2many('toonproject.asset', string="Материалы")
    
    # price (calculate)
    # last_status (calculate?)

    