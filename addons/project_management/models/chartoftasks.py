from odoo import fields, models, api

class ChartOfTasks(models.Model):
    _name = 'chartoftasks'
    _description = 'Biểu đồ tiến độ công việc'

    cong_viec_id = fields.Many2one('cong_viec', string='Tiến độ công việc', ondelete='cascade')
