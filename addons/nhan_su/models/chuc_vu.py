# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Chức vụ của nhân viên'
    _rec_name = 'ten_chuc_vu'

    # Mã chức vụ - tự động tạo bằng sequence
    ma_chuc_vu = fields.Char(
        string="Mã chức vụ",
        readonly=True,
        copy=False,
        default=lambda self: 'Mới'
    )
    ten_chuc_vu = fields.Char(string="Tên chức vụ", required=True)
    mo_ta = fields.Text(string="Mô tả")

    # One2many liên kết với nhân viên - suffix _ids
    nhan_vien_ids = fields.One2many(
        'nhan_vien',
        'chuc_vu_id',
        string='Danh sách nhân viên'
    )

    @api.model
    def create(self, vals):
        """Tự động tạo mã chức vụ khi tạo mới"""
        if vals.get('ma_chuc_vu', 'Mới') == 'Mới':
            vals['ma_chuc_vu'] = self.env['ir.sequence'].next_by_code('chuc_vu.sequence') or 'CV001'
        return super(ChucVu, self).create(vals)

    def name_get(self):
        """Hiển thị tên chức vụ"""
        result = []
        for record in self:
            name = record.ten_chuc_vu or record.ma_chuc_vu or f'Chức vụ #{record.id}'
            result.append((record.id, name))
        return result
