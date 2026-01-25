# -*- coding: utf-8 -*-
{
    'name': "Quản lý Công việc",

    'summary': """
        Module quản lý công việc, dự án, nhiệm vụ và theo dõi tiến độ""",

    'description': """
        Module quản lý công việc bao gồm:
        - Quản lý dự án
        - Quản lý công việc
        - Phân công nhiệm vụ
        - Theo dõi tiến độ
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Project Management',
    'version': '1.0',

    'depends': ['base', 'nhan_su', 'project_management'],  # Phụ thuộc vào module nhan_su và project_management

    # Data files được load theo thứ tự
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data (sequences phải load trước views)
        'data/sequence_data.xml',
        # Views
        'views/cong_viec.xml',
        'views/nhiem_vu.xml',
        'views/tien_do.xml',
        'views/bao_cao_hieu_qua.xml',
        'views/nhan_vien_extend.xml',
        'views/menu.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
