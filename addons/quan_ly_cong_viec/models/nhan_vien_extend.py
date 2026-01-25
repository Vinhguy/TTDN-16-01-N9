# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NhanVienExtend(models.Model):
    """Kế thừa model nhan_vien để thêm thông tin từ module quan_ly_cong_viec"""
    _inherit = 'nhan_vien'
    
    # Các nhiệm vụ được giao
    nhiem_vu_duoc_giao_ids = fields.One2many(
        'nhiem_vu',
        'nguoi_thuc_hien_id',
        string='Nhiệm vụ được giao'
    )
    
    # Các dự án tham gia - sử dụng model projects từ project_management
    du_an_tham_gia_ids = fields.Many2many(
        'projects',
        'projects_nhan_vien_rel',
        'nhan_vien_id',
        'projects_id',
        string='Dự án tham gia'
    )
    
    # Thống kê
    so_nhiem_vu_dang_thuc_hien = fields.Integer(
        string='Số nhiệm vụ đang làm',
        compute='_compute_thong_ke_nhiem_vu',
        store=False
    )
    
    so_nhiem_vu_hoan_thanh = fields.Integer(
        string='Số nhiệm vụ hoàn thành',
        compute='_compute_thong_ke_nhiem_vu',
        store=False
    )
    
    @api.depends('nhiem_vu_duoc_giao_ids', 'nhiem_vu_duoc_giao_ids.trang_thai')
    def _compute_thong_ke_nhiem_vu(self):
        """Thống kê nhiệm vụ của nhân viên"""
        for record in self:
            record.so_nhiem_vu_dang_thuc_hien = len(
                record.nhiem_vu_duoc_giao_ids.filtered(
                    lambda n: n.trang_thai == 'dang_thuc_hien'
                )
            )
            record.so_nhiem_vu_hoan_thanh = len(
                record.nhiem_vu_duoc_giao_ids.filtered(
                    lambda n: n.trang_thai == 'hoan_thanh'
                )
            )
