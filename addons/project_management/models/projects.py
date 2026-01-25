from odoo import models, fields, api
from datetime import date, datetime

class Projects(models.Model):
    _name = 'projects'
    _description = 'Quản lý dự án'

    projects_id = fields.Char("Mã dự án", required=True, copy=False, readonly=True, default='New')
    projects_name = fields.Char("Tên dự án")
    
    manager_name = fields.Many2one('nhan_vien', string="Quản lý dự án")

    start_date = fields.Date("Ngày bắt đầu")
    actual_end_date = fields.Date("Ngày kết thúc thực tế")

    progress = fields.Float("Tiến độ (%)", compute='_compute_progress', store=True)
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

    task_ids = fields.One2many('taskss', inverse_name='projects_id', String='Công việc') 

    @api.depends('task_ids.status')
    def _compute_progress(self):
        for project in self:
            total_tasks = len(project.task_ids)
            completed_tasks = len(project.task_ids.filtered(lambda task: task.status == 'completed'))
            
            if total_tasks > 0:
                project.progress = (completed_tasks / total_tasks) * 100
            else:
                project.progress = 0


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
        self.ensure_one()  # Đảm bảo phương thức chỉ xử lý một bản ghi
        return {
            'type': 'ir.actions.act_window',
            'name': 'Biểu Đồ Công Việc Công Việc',
            'res_model': 'taskss',
            'view_mode': 'graph',
            'domain': [('projects_id', '=', self.id)],  # Lọc công việc theo dự án hiện tại
            # Đặt giá trị mặc định cho trường projects_id
            'context': {'search_default_group_by_projects_id': self.id},
            'target': 'current',
        }