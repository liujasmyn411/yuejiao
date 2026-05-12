"""
粤教服务 - 数据模型层
定义所有SQLAlchemy ORM模型类
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, REAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# 基类，所有模型的父类
Base = declarative_base()


# ========== 表1：统一用户表 ==========
class SysUser(Base):
    __tablename__ = "sys_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    real_name = Column(String, nullable=False)
    user_type = Column(String, nullable=False)    # STUDENT 学生 / EMPLOYEE 员工
    employee_role = Column(String)                 # 员工角色
    department = Column(String)
    contact_info = Column(String)
    status = Column(String, default="正常")
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ========== 表2：学生行政服务表 ==========
class StudentAdminService(Base):
    __tablename__ = "student_admin_service"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, nullable=False)
    service_type = Column(String, nullable=False)  # 请假 / 考务查询
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    reason = Column(Text)
    status = Column(String, default="待审批")
    approver_id = Column(Integer)
    related_academic_id = Column(Integer)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ========== 表3：心理健康画像表 ==========
class StudentPsychProfile(Base):
    __tablename__ = "student_psych_profile"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, nullable=False, unique=True)
    latest_emotion_tag = Column(String)    # 焦虑 / 平稳
    emotion_score = Column(Integer)        # 0-100
    last_interaction_time = Column(DateTime)
    emotion_history = Column(Text)         # JSON字符串存历史
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ========== 表4：心理预警表 ==========
class StudentPsychAlert(Base):
    __tablename__ = "student_psych_alert"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, nullable=False)
    trigger_reason = Column(Text, nullable=False)
    risk_level = Column(String, nullable=False)  # 高 / 中 / 低
    status = Column(String, default="未处理")
    teacher_id = Column(Integer)
    create_time = Column(DateTime, default=datetime.now)


# ========== 表5：售后反馈工单表 ==========
class StudentFeedbackTicket(Base):
    __tablename__ = "student_feedback_ticket"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    detail = Column(Text)
    status = Column(String, default="待处理")
    solution = Column(Text)
    is_notified = Column(Integer, default=0)  # 0未通知 1已通知
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ========== 表6：意向客户表 ==========
class CrmLead(Base):
    __tablename__ = "crm_lead"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String, nullable=False)
    contact_info = Column(String)
    background_info = Column(Text)
    follow_up_history = Column(Text)  # JSON或长文本
    status = Column(String, default="新增意向")
    owner_employee_id = Column(Integer, nullable=False)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ========== 表7：员工日报表 ==========
class EmployeeDailyReport(Base):
    __tablename__ = "employee_daily_report"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, nullable=False)
    report_date = Column(String)  # 用字符串存日期: 2026-05-12
    content = Column(Text, nullable=False)
    create_time = Column(DateTime, default=datetime.now)


# ========== 表8：学生成绩表 ==========
class StudentScore(Base):
    __tablename__ = "student_score"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, nullable=False)
    course_name = Column(String, nullable=False)
    score = Column(REAL, nullable=False)
    semester = Column(String)
    create_time = Column(DateTime, default=datetime.now)


# ========== 表9：课程与项目表 ==========
class CourseProject(Base):
    __tablename__ = "course_project"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String, nullable=False)
    category = Column(String)       # 新加坡-本科 / 德国-双元制
    description = Column(Text)
    target_audience = Column(Text)


# ========== 表10：活动与讲座表 ==========
class EventLecture(Base):
    __tablename__ = "event_lecture"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String, nullable=False)
    event_type = Column(String)     # 线上 / 线下
    start_time = Column(DateTime)
    location = Column(String)
    max_participants = Column(Integer)
    current_participants = Column(Integer, default=0)


# ========== 表11：活动报名表 ==========
class EventRegistration(Base):
    __tablename__ = "event_registration"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("event_lecture.id"))
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String)
    status = Column(String, default="已报名")
    create_time = Column(DateTime, default=datetime.now)
