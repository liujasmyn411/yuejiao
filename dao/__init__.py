"""
粤教服务 - DAO数据访问层
封装所有数据库的增删改查操作
"""

from sqlalchemy.orm import Session
from datetime import datetime

from model import (
    SysUser, EventLecture, EventRegistration, CourseProject,
    CrmLead, EmployeeDailyReport, StudentScore,
    StudentAdminService, StudentPsychProfile, StudentPsychAlert,
    StudentFeedbackTicket
)


class UserDAO:
    """用户数据访问对象"""

    @staticmethod
    def get_by_username(db: Session, username: str):
        """根据用户名查询用户"""
        return db.query(SysUser).filter(SysUser.username == username, SysUser.delete_flag == 0).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int):
        """根据ID查询用户"""
        return db.query(SysUser).filter(SysUser.id == user_id, SysUser.delete_flag == 0).first()

    @staticmethod
    def create(db: Session, **kwargs):
        """创建用户"""
        user = SysUser(**kwargs)
        db.add(user)
        return user

    @staticmethod
    def update_login_info(db: Session, user_id: int, login_ip: str = ""):
        """更新登录信息"""
        user = db.query(SysUser).filter(SysUser.id == user_id).first()
        if user:
            user.last_login_time = datetime.now()
            user.last_login_ip = login_ip
        return user


class EventDAO:
    """活动数据访问对象"""

    @staticmethod
    def get_all(db: Session):
        """获取所有活动"""
        return db.query(EventLecture).filter(EventLecture.delete_flag == 0).order_by(EventLecture.start_time).all()

    @staticmethod
    def get_upcoming(db: Session, limit: int = 5):
        """获取即将开始的活动"""
        return db.query(EventLecture).filter(
            EventLecture.start_time > datetime.now(),
            EventLecture.delete_flag == 0
        ).order_by(EventLecture.start_time).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, event_id: int):
        """获取单个活动"""
        return db.query(EventLecture).filter(EventLecture.id == event_id, EventLecture.delete_flag == 0).first()

    @staticmethod
    def create_registration(db: Session, event_id: int, customer_id: int, customer_name: str = "", contact: str = ""):
        """创建活动报名"""
        reg = EventRegistration(
            event_id=event_id,
            customer_id=customer_id,
            customer_name=customer_name,
            contact=contact
        )
        db.add(reg)
        return reg

    @staticmethod
    def increment_participants(db: Session, event_id: int):
        """增加报名人数"""
        event = db.query(EventLecture).filter(EventLecture.id == event_id).first()
        if event:
            event.current_participants = (event.current_participants or 0) + 1
        return event


class ProjectDAO:
    """项目数据访问对象"""

    @staticmethod
    def get_all(db: Session, category: str = ""):
        """获取所有项目（可选按分类筛选）"""
        query = db.query(CourseProject).filter(CourseProject.delete_flag == 0)
        if category:
            query = query.filter(CourseProject.category.contains(category))
        return query.order_by(CourseProject.sort_order).all()


class CrmDAO:
    """CRM意向客户数据访问对象"""

    @staticmethod
    def get_all(db: Session, status: str = "", keyword: str = ""):
        """获取意向客户列表"""
        query = db.query(CrmLead).filter(CrmLead.delete_flag == 0)
        if status:
            query = query.filter(CrmLead.status == status)
        if keyword:
            query = query.filter(CrmLead.customer_name.contains(keyword))
        return query.order_by(CrmLead.create_time.desc()).limit(50).all()

    @staticmethod
    def get_by_id(db: Session, lead_id: int):
        """根据ID获取客户"""
        return db.query(CrmLead).filter(CrmLead.id == lead_id, CrmLead.delete_flag == 0).first()

    @staticmethod
    def create(db: Session, **kwargs):
        """新增意向客户"""
        lead = CrmLead(**kwargs)
        db.add(lead)
        return lead

    @staticmethod
    def update(db: Session, lead_id: int, **kwargs):
        """更新客户信息"""
        lead = db.query(CrmLead).filter(CrmLead.id == lead_id).first()
        if lead:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(lead, key, value)
        return lead


class ReportDAO:
    """日报数据访问对象"""

    @staticmethod
    def create(db: Session, employee_id: int, content: str, report_date: str, work_type: str = ""):
        """提交日报"""
        report = EmployeeDailyReport(
            employee_id=employee_id,
            content=content,
            report_date=report_date,
            work_type=work_type
        )
        db.add(report)
        return report

    @staticmethod
    def get_all(db: Session, date: str = "", employee_id: int = 0):
        """查询日报"""
        query = db.query(EmployeeDailyReport).filter(EmployeeDailyReport.delete_flag == 0)
        if date:
            query = query.filter(EmployeeDailyReport.report_date == date)
        if employee_id:
            query = query.filter(EmployeeDailyReport.employee_id == employee_id)
        return query.order_by(EmployeeDailyReport.create_time.desc()).limit(30).all()


class ScoreDAO:
    """成绩数据访问对象"""

    @staticmethod
    def create(db: Session, **kwargs):
        """录入成绩"""
        record = StudentScore(**kwargs)
        db.add(record)
        return record

    @staticmethod
    def get_all(db: Session, student_id: int = 0):
        """查询成绩"""
        query = db.query(StudentScore).filter(StudentScore.delete_flag == 0)
        if student_id:
            query = query.filter(StudentScore.student_id == student_id)
        return query.order_by(StudentScore.create_time.desc()).all()


class StudentServiceDAO:
    """学生行政服务数据访问对象"""

    @staticmethod
    def create_leave(db: Session, student_id: int, service_type: str, start_time: datetime, end_time: datetime, reason: str, leave_type: str = ""):
        """提交请假申请"""
        leave = StudentAdminService(
            student_id=student_id,
            service_type=service_type,
            leave_type=leave_type,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            status="待审批"
        )
        db.add(leave)
        return leave

    @staticmethod
    def get_leaves(db: Session, student_id: int = 0):
        """查询请假记录"""
        query = db.query(StudentAdminService).filter(
            StudentAdminService.service_type == "请假",
            StudentAdminService.delete_flag == 0
        )
        if student_id:
            query = query.filter(StudentAdminService.student_id == student_id)
        return query.order_by(StudentAdminService.create_time.desc()).all()


class FeedbackDAO:
    """投诉反馈数据访问对象"""

    @staticmethod
    def create(db: Session, student_id: int, content: str, detail: str = "", feedback_type: str = "咨询", urgency_level: str = "中"):
        """提交投诉反馈"""
        ticket = StudentFeedbackTicket(
            student_id=student_id,
            feedback_type=feedback_type,
            content=content,
            detail=detail,
            urgency_level=urgency_level,
            status="待处理"
        )
        db.add(ticket)
        return ticket

    @staticmethod
    def get_all(db: Session, student_id: int = 0):
        """查询投诉反馈"""
        query = db.query(StudentFeedbackTicket).filter(StudentFeedbackTicket.delete_flag == 0)
        if student_id:
            query = query.filter(StudentFeedbackTicket.student_id == student_id)
        return query.order_by(StudentFeedbackTicket.create_time.desc()).all()


class PsychAlertDAO:
    """心理预警数据访问对象"""

    @staticmethod
    def create(db: Session, student_id: int, trigger_reason: str, risk_level: str, alert_source: str = "聊天对话"):
        """提交心理预警"""
        alert = StudentPsychAlert(
            student_id=student_id,
            trigger_reason=trigger_reason,
            risk_level=risk_level,
            alert_source=alert_source,
            status="未处理"
        )
        db.add(alert)
        return alert

    @staticmethod
    def get_all(db: Session, risk_level: str = ""):
        """查询心理预警"""
        query = db.query(StudentPsychAlert).filter(StudentPsychAlert.delete_flag == 0)
        if risk_level:
            query = query.filter(StudentPsychAlert.risk_level == risk_level)
        return query.order_by(StudentPsychAlert.create_time.desc()).all()

    @staticmethod
    def update_profile(db: Session, student_id: int, risk_level: str):
        """更新心理画像"""
        profile = db.query(StudentPsychProfile).filter(
            StudentPsychProfile.student_id == student_id,
            StudentPsychProfile.delete_flag == 0
        ).first()

        if profile:
            profile.latest_emotion_tag = risk_level
            profile.risk_level = "high" if risk_level == "高" else ("medium" if risk_level == "中" else "low")
            profile.emotion_score = 20 if risk_level == "高" else (40 if risk_level == "中" else 60)
            profile.total_risk_count = (profile.total_risk_count or 0) + 1
            profile.teacher_follow_up_status = "未跟进"
            profile.last_interaction_time = datetime.now()
        else:
            new_profile = StudentPsychProfile(
                student_id=student_id,
                latest_emotion_tag=risk_level,
                risk_level="high" if risk_level == "高" else ("medium" if risk_level == "中" else "low"),
                emotion_score=20 if risk_level == "高" else 40,
                total_risk_count=1,
                teacher_follow_up_status="未跟进",
                last_interaction_time=datetime.now()
            )
            db.add(new_profile)


class DashboardDAO:
    """仪表盘数据访问对象"""

    @staticmethod
    def get_stats(db: Session):
        """获取统计数据"""
        # 客户统计
        total_leads = db.query(CrmLead).filter(CrmLead.delete_flag == 0).count()
        status_counts = {}
        for s in ["新增意向", "跟进中", "已签约", "已流失"]:
            status_counts[s] = db.query(CrmLead).filter(CrmLead.status == s, CrmLead.delete_flag == 0).count()

        # 投诉统计
        total_tickets = db.query(StudentFeedbackTicket).filter(StudentFeedbackTicket.delete_flag == 0).count()
        pending_tickets = db.query(StudentFeedbackTicket).filter(
            StudentFeedbackTicket.status == "待处理",
            StudentFeedbackTicket.delete_flag == 0
        ).count()

        # 心理预警统计
        high_risk = db.query(StudentPsychAlert).filter(StudentPsychAlert.risk_level == "高", StudentPsychAlert.delete_flag == 0).count()
        medium_risk = db.query(StudentPsychAlert).filter(StudentPsychAlert.risk_level == "中", StudentPsychAlert.delete_flag == 0).count()

        # 日报统计
        today = datetime.now().strftime("%Y-%m-%d")
        today_reports = db.query(EmployeeDailyReport).filter(
            EmployeeDailyReport.report_date == today,
            EmployeeDailyReport.delete_flag == 0
        ).count()

        return {
            "customers": {"total": total_leads, "by_status": status_counts},
            "feedback": {"total": total_tickets, "pending": pending_tickets},
            "psych_alerts": {"high": high_risk, "medium": medium_risk},
            "daily_reports": {"today": today_reports}
        }
