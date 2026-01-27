# -*- coding: utf-8 -*-
def migrate(cr, version):
    """
    Migration script để đổi tên cột du_an_id thành projects_id
    trong bảng cong_viec
    """
    # Kiểm tra xem cột du_an_id có tồn tại không
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='cong_viec' AND column_name='du_an_id'
    """)
    
    if cr.fetchone():
        # Đổi tên cột du_an_id thành projects_id
        cr.execute("""
            ALTER TABLE cong_viec 
            RENAME COLUMN du_an_id TO projects_id
        """)
        print("✅ Đã đổi tên cột du_an_id → projects_id trong bảng cong_viec")
    else:
        print("ℹ️ Cột du_an_id không tồn tại, bỏ qua migration")
