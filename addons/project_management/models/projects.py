from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class Projects(models.Model):
    _name = 'projects'
    _description = 'Quản lý dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    projects_id = fields.Char("Mã dự án", required=True, copy=False, readonly=True, default='New')
    projects_name = fields.Char("Tên dự án")
    
    manager_name = fields.Many2one('nhan_vien', string="Quản lý dự án")

    start_date = fields.Date("Ngày bắt đầu")
    actual_end_date = fields.Date("Ngày kết thúc thực tế")

    progress = fields.Float(
        "Tiến độ (%)",
        compute='_compute_progress',
        inverse='_inverse_progress',
        store=True,
        help="Tiến độ dự án (0-100%). Có thể nhập tay, nhưng sẽ được tính lại khi danh sách công việc thay đổi."
    )
    status = fields.Selection(
        selection=[
            ('not_started', 'Chưa bắt đầu'),
            ('in_progress', 'Đang thực hiện'),
            ('completed', 'Hoàn thành'),
            ('delayed', 'Trì hoãn'),
            ('cancelled', 'Hủy bỏ')
        ], 
        string='Trạng thái', store=True
    )

    ly_do_1 = fields.Text(string="Lý do hủy bỏ", help="Lý do hủy bỏ công việc")

    task_ids = fields.One2many(
        'cong_viec', 
        'du_an_id', 
        string='Công việc',
        help='Danh sách công việc thuộc dự án này (field du_an_id được thêm bởi module project_management)'
    )

    # ============ TRƯỜNG XÉT DUYỆT DỰ ÁN ============
    approval_state = fields.Selection([
        ('draft', 'Nháp'),
        ('pending', 'Chờ xét duyệt'),
        ('approved', 'Đã phê duyệt'),
        ('rejected', 'Từ chối')
    ], string='Trạng thái duyệt', default='draft', tracking=True)
    
    approver_id = fields.Many2one('nhan_vien', string='Người phê duyệt', readonly=True)
    approval_date = fields.Datetime(string='Ngày phê duyệt', readonly=True)
    approval_signature = fields.Binary(string='Chữ ký phê duyệt')
    rejection_reason = fields.Text(string='Lý do từ chối') 

    @api.depends('task_ids.trang_thai', 'task_ids.ti_le_hoan_thanh')
    def _compute_progress(self):
        """Tính tiến độ dự án từ công việc (cong_viec)"""
        for project in self:
            if project.task_ids:
                # Tính trung bình tỷ lệ hoàn thành của tất cả công việc
                total_progress = sum(project.task_ids.mapped('ti_le_hoan_thanh'))
                project.progress = total_progress / len(project.task_ids)
            else:
                project.progress = 0.0

    def _inverse_progress(self):
        """Cho phép người dùng nhập/sửa trực tiếp tiến độ dự án trên form.

        Giá trị người dùng nhập sẽ được lưu lại.
        Khi danh sách công việc hoặc % hoàn thành công việc thay đổi,
        hàm compute vẫn sẽ tính lại để đồng bộ theo công việc.
        """
        # Không cần xử lý gì thêm, Odoo sẽ tự ghi giá trị `progress`
        # được người dùng nhập vào record.
        for project in self:
            project.progress = project.progress


    def name_get(self):
        result = []
        for record in self:
            name = f"{record.projects_id}"

            result.append((record.id, name))
        return result
    
    budget_ids = fields.One2many('budgets', inverse_name='projects_id', string="Ngân sách Dự án")

    @api.model
    def _get_next_project_code(self):
        """Lấy mã dự án tiếp theo chưa sử dụng trong database"""
        sequence = self.env['ir.sequence'].search([('code', '=', 'projects.code')], limit=1)
        if sequence:
            # Lấy số tiếp theo từ sequence
            next_number = sequence.number_next
            # Tạo mã dự án dự kiến
            prefix = sequence.prefix or 'DA'
            padding = sequence.padding or 5
            next_code = f"{prefix}{str(next_number).zfill(padding)}"
            
            # Kiểm tra xem mã này đã tồn tại trong database chưa
            while self.search([('projects_id', '=', next_code)], limit=1):
                next_number += 1
                next_code = f"{prefix}{str(next_number).zfill(padding)}"
            
            return next_code
        return 'DA00001'

    @api.model
    def default_get(self, fields_list):
        """Hiển thị preview mã dự án trong form KHÔNG tăng sequence"""
        res = super(Projects, self).default_get(fields_list)
        if 'projects_id' in fields_list:
            res['projects_id'] = self._get_next_project_code()
        return res

    @api.model
    def create(self, vals):
        """Tự động sinh mã dự án khi lưu và đồng bộ sequence"""
        if not vals.get('projects_id') or vals.get('projects_id') == 'New':
            # Lấy mã tiếp theo chưa sử dụng
            next_code = self._get_next_project_code()
            vals['projects_id'] = next_code
            
            # Đồng bộ sequence với số vừa sử dụng
            sequence = self.env['ir.sequence'].search([('code', '=', 'projects.code')], limit=1)
            if sequence:
                # Lấy số từ mã vừa tạo (bỏ prefix)
                used_number = int(next_code.replace(sequence.prefix or 'DA', ''))
                # Cập nhật sequence để số tiếp theo là used_number + 1
                if used_number >= sequence.number_next:
                    sequence.write({'number_next': used_number + 1})
        
        return super(Projects, self).create(vals)

    def action_view_task_chart(self):
        """Xem biểu đồ công việc - sử dụng cong_viec"""
        self.ensure_one()  # Đảm bảo phương thức chỉ xử lý một bản ghi
        return {
            'type': 'ir.actions.act_window',
            'name': 'Biểu Đồ Công Việc',
            'res_model': 'cong_viec',
            'view_mode': 'graph',
            'domain': [('du_an_id', '=', self.id)],  # Lọc công việc theo dự án hiện tại
            'context': {'search_default_group_by_du_an_id': self.id},
            'target': 'current',
        }

    # ============ CÁC PHƯƠNG THỨC XÉT DUYỆT ============
    def action_submit_approval(self):
        """Gửi dự án đi xét duyệt"""
        for record in self:
            if not record.manager_name:
                raise UserError('Vui lòng chọn Quản lý dự án trước khi gửi xét duyệt!')
            record.approval_state = 'pending'

    def action_approve(self):
        """Phê duyệt dự án - yêu cầu có chữ ký"""
        for record in self:
            if not record.approval_signature:
                raise UserError('Vui lòng ký tên trước khi phê duyệt!')
            record.write({
                'approval_state': 'approved',
                'approver_id': record.manager_name.id,
                'approval_date': fields.Datetime.now(),
            })
            # Tự động tạo công việc cốt lõi khi phê duyệt
            record._create_core_tasks()

    def _create_core_tasks(self):
        """Tạo các công việc cốt lõi cho dự án đã được phê duyệt"""
        self.ensure_one()
        
        # Kiểm tra module quan_ly_cong_viec có được cài đặt
        try:
            CongViec = self.env['cong_viec']
        except KeyError:
            # Module chưa cài, bỏ qua
            _logger.warning(f"Module quan_ly_cong_viec chưa được cài đặt. Không thể tạo công việc tự động cho dự án {self.projects_id}")
            return
        
        # Kiểm tra manager_name (required field)
        if not self.manager_name:
            _logger.warning(f"Dự án {self.projects_id} không có quản lý dự án. Không thể tạo công việc tự động.")
            return  # Không có manager, không thể tạo công việc
        
        # Danh sách 5 công việc cốt lõi
        core_tasks = [
            {'ten': 'Khởi động dự án và thống nhất phạm vi', 'uu_tien': 'cao'},
            {'ten': 'Lên kế hoạch và phân bổ nguồn lực', 'uu_tien': 'cao'},
            {'ten': 'Kiểm tra chất lượng', 'uu_tien': 'trung_binh'},
            {'ten': 'Báo cáo định kỳ', 'uu_tien': 'trung_binh'},
            {'ten': 'Đóng gói và bàn giao', 'uu_tien': 'cao'},
        ]
        
        # Tạo công việc với error handling
        created_count = 0
        created_tasks = []
        for task in core_tasks:
            try:
                new_task = CongViec.create({
                    'ten_cong_viec': task['ten'],
                    'du_an_id': self.id,
                    'muc_do_uu_tien': task['uu_tien'],
                    'trang_thai': 'moi',
                    'nguoi_phu_trach_id': self.manager_name.id,
                    'ngay_bat_dau': self.start_date,
                    'ngay_ket_thuc': self.actual_end_date,
                })
                created_tasks.append(new_task)
                created_count += 1
            except Exception as e:
                # Log lỗi nhưng không dừng quá trình
                _logger.error(f"Lỗi khi tạo công việc '{task['ten']}' cho dự án {self.projects_id}: {str(e)}")
        


    def action_reject(self):
        """Từ chối dự án"""
        for record in self:
            if not record.rejection_reason:
                raise UserError('Vui lòng nhập lý do từ chối!')
            record.approval_state = 'rejected'

    def action_reset_draft(self):
        """Đặt lại trạng thái nháp"""
        for record in self:
            record.write({
                'approval_state': 'draft',
                'approval_signature': False,
                'approver_id': False,
                'approval_date': False,
                'rejection_reason': False,
            })

    def action_print_approval_pdf(self):
        """In báo cáo phê duyệt dự án dạng PDF"""
        self.ensure_one()
        if self.approval_state != 'approved':
            raise UserError('Chỉ có thể in báo cáo cho dự án đã được phê duyệt!')
        return self.env.ref('project_management.action_report_project_approval').report_action(self)