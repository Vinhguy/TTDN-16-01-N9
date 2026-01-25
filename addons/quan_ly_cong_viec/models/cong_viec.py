# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CongViec(models.Model):
    _name = 'cong_viec'
    _description = 'Bảng quản lý công việc'
    _rec_name = 'ten_cong_viec'

    # Mã công việc - tự động tạo bằng sequence
    ma_cong_viec = fields.Char(
        string="Mã công việc",
        readonly=True,
        copy=False,
        default=lambda self: 'Mới'
    )
    
    ten_cong_viec = fields.Char(string="Tên công việc", required=True)
    mo_ta = fields.Text(string="Mô tả")
    ngay_bat_dau = fields.Date(string="Ngày bắt đầu")
    ngay_ket_thuc = fields.Date(string="Ngày kết thúc")
    muc_do_uu_tien = fields.Selection(
        selection=[
            ('thap', 'Thấp'),
            ('trung_binh', 'Trung bình'),
            ('cao', 'Cao'),
            ('khan_cap', 'Khẩn cấp'),
        ],
        string="Mức độ ưu tiên",
        default='trung_binh'
    )
    trang_thai = fields.Selection(
        selection=[
            ('moi', 'Mới'),
            ('dang_thuc_hien', 'Đang thực hiện'),
            ('hoan_thanh', 'Hoàn thành'),
            ('tam_dung', 'Tạm dừng'),
        ],
        string="Trạng thái",
        default='moi'
    )
    
    # Liên kết Many2one tới model projects từ project_management
    du_an_id = fields.Many2one('projects', string='Dự án', ondelete='cascade', help='Dự án từ module Project Management')
    
    # ============ TÍCH HỢP VỚI MODULE NHÂN SỰ ============
    # Người phụ trách công việc
    nguoi_phu_trach_id = fields.Many2one(
        'nhan_vien',
        string='Người phụ trách',
        required=True,
        ondelete='restrict',
        help='Nhân viên chịu trách nhiệm công việc này'
    )
    
    # Nhân viên được phân công (Many2many)
    nhan_vien_phan_cong_ids = fields.Many2many(
        'nhan_vien',
        'cong_viec_nhan_vien_rel',
        'cong_viec_id',
        'nhan_vien_id',
        string='Nhân viên thực hiện',
        help='Danh sách nhân viên được phân công'
    )
    
    # Giờ làm dự kiến và thực tế
    gio_lam_du_kien = fields.Float(string='Giờ làm dự kiến')
    gio_lam_thuc_te = fields.Float(string='Giờ làm thực tế', default=0.0)
    
    # Tỷ lệ hoàn thành tự động
    ti_le_hoan_thanh = fields.Float(
        string='Tỷ lệ hoàn thành (%)',
        compute='_compute_ti_le_hoan_thanh',
        store=True
    )
    
    # Liên kết One2many - suffix _ids
    nhiem_vu_ids = fields.One2many(
        'nhiem_vu',
        'cong_viec_id',
        string='Danh sách nhiệm vụ'
    )
    
    @api.depends('nhiem_vu_ids.trang_thai', 'nhiem_vu_ids.ti_le_hoan_thanh')
    def _compute_ti_le_hoan_thanh(self):
        """Tính tỷ lệ hoàn thành từ nhiệm vụ"""
        for record in self:
            if record.nhiem_vu_ids:
                total_progress = sum(record.nhiem_vu_ids.mapped('ti_le_hoan_thanh'))
                record.ti_le_hoan_thanh = total_progress / len(record.nhiem_vu_ids)
            else:
                record.ti_le_hoan_thanh = 0.0

    @api.model
    def create(self, vals):
        """Tự động tạo mã công việc khi tạo mới"""
        if vals.get('ma_cong_viec', 'Mới') == 'Mới':
            vals['ma_cong_viec'] = self.env['ir.sequence'].next_by_code('cong_viec.sequence') or 'CV001'
        return super(CongViec, self).create(vals)

    def name_get(self):
        """Hiển thị mã và tên công việc"""
        result = []
        for record in self:
            if record.ten_cong_viec:
                name = f"{record.ma_cong_viec} - {record.ten_cong_viec}"
            else:
                name = record.ma_cong_viec or f'Công việc #{record.id}'
            result.append((record.id, name))
        return result
