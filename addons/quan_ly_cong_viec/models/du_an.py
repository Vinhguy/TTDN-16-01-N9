# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DuAn(models.Model):
    _name = 'du_an'
    _description = 'Bảng quản lý dự án'
    _rec_name = 'ten_du_an'

    # Mã dự án - tự động tạo bằng sequence
    ma_du_an = fields.Char(
        string="Mã dự án",
        readonly=True,
        copy=False,
        default=lambda self: 'Mới'
    )
    
    ten_du_an = fields.Char(string="Tên dự án", required=True)
    mo_ta = fields.Text(string="Mô tả")
    ngay_bat_dau = fields.Date(string="Ngày bắt đầu")
    ngay_ket_thuc = fields.Date(string="Ngày kết thúc")
    trang_thai = fields.Selection(
        selection=[
            ('moi', 'Mới'),
            ('dang_thuc_hien', 'Đang thực hiện'),
            ('hoan_thanh', 'Hoàn thành'),
            ('tam_dung', 'Tạm dừng'),
            ('huy', 'Hủy'),
        ],
        string="Trạng thái",
        default='moi'
    )
    
    # ============ TÍCH HỢP VỚI MODULE NHÂN SỰ ============
    # Quản lý dự án - sử dụng dữ liệu nhân viên từ module nhan_su
    quan_ly_du_an_id = fields.Many2one(
        'nhan_vien',
        string='Quản lý dự án',
        required=True,
        ondelete='restrict',
        help='Nhân viên quản lý dự án này'
    )
    
    # Phòng ban thực hiện
    phong_ban_thuc_hien_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban thực hiện',
        ondelete='set null',
        help='Phòng ban chịu trách nhiệm thực hiện dự án'
    )
    
    # Thành viên tham gia dự án (Many2many)
    thanh_vien_ids = fields.Many2many(
        'nhan_vien',
        'du_an_nhan_vien_rel',
        'du_an_id',
        'nhan_vien_id',
        string='Thành viên dự án',
        help='Danh sách nhân viên tham gia dự án'
    )
    
    # Tính toán số lượng thành viên
    so_luong_thanh_vien = fields.Integer(
        string='Số thành viên',
        compute='_compute_so_luong_thanh_vien',
        store=True
    )
    
    # Ngân sách dự án
    ngan_sach = fields.Float(string='Ngân sách (VND)', default=0.0)
    chi_phi_thuc_te = fields.Float(string='Chi phí thực tế (VND)', default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    # Tỷ lệ hoàn thành tự động tính từ công việc
    ti_le_hoan_thanh = fields.Float(
        string='Tỷ lệ hoàn thành (%)',
        compute='_compute_ti_le_hoan_thanh',
        store=True
    )
    
    # Liên kết One2many - suffix _ids
    cong_viec_ids = fields.One2many(
        'cong_viec',
        'du_an_id',
        string='Danh sách công việc'
    )
    
    # ============ CÁC HÀM TÍNH TOÁN ============
    @api.depends('thanh_vien_ids')
    def _compute_so_luong_thanh_vien(self):
        """Tính số lượng thành viên trong dự án"""
        for record in self:
            record.so_luong_thanh_vien = len(record.thanh_vien_ids)
    
    @api.depends('cong_viec_ids.trang_thai')
    def _compute_ti_le_hoan_thanh(self):
        """Tính tỷ lệ hoàn thành dựa trên công việc"""
        for record in self:
            total = len(record.cong_viec_ids)
            if total > 0:
                completed = len(record.cong_viec_ids.filtered(lambda c: c.trang_thai == 'hoan_thanh'))
                record.ti_le_hoan_thanh = (completed / total) * 100
            else:
                record.ti_le_hoan_thanh = 0.0

    @api.model
    def create(self, vals):
        """Tự động tạo mã dự án khi tạo mới"""
        if vals.get('ma_du_an', 'Mới') == 'Mới':
            vals['ma_du_an'] = self.env['ir.sequence'].next_by_code('du_an.sequence') or 'DA001'
        return super(DuAn, self).create(vals)

    def name_get(self):
        """Hiển thị mã và tên dự án"""
        result = []
        for record in self:
            if record.ten_du_an:
                name = f"{record.ma_du_an} - {record.ten_du_an}"
            else:
                name = record.ma_du_an or f'Dự án #{record.id}'
            result.append((record.id, name))
        return result
