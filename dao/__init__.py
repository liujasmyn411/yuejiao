"""
粤教服务 - DAO数据访问层
封装所有数据库的增删改查操作
"""

from sqlalchemy.orm import Session
from datetime import datetime

from model import (
    EventLecture, EventRegistration, CourseProject,
    CrmLead, EmployeeDailyReport, StudentScore,
    StudentAdminService, StudentPsychProfile, StudentPsychAlert,
    StudentFeedbackTicket
)


class EventDAO:
    """活动数据访问对象"""

    @staticmethod
    def get_all(db: Session):
        """获取所有活动"""
        return db.query(EventLecture).order_by(EventLecture.start_time).all()

    @staticmethod
    def get_upcoming(db: Session, limit: int = 5):
        """获取即将开始的活动"""
        return db.query(EventLecture).filter(
            EventLecture.start_time > datetime.now()
        ).order_by(EventLecture.start_time).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, event_id: int):
        """获取单个活动"""
        return db.query(EventLecture).filter(EventLecture.id == event_id).first()

    @staticmethod
    def create_registration(db: Session, event_id: int, customer_name: str, customer_phone: str):
        """创建活动报名"""
        reg = EventRegistration(
            event_id=event_id,
            customer_name=customer_name,
            customer_phone=customer_phone
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
        query = db.query(CourseProject)
        if category:
            query = query.filter(CourseProject.category.contains(category))
        return query.all()


class CrmDAO:
    """CRM意向客户数据访问对象"""

    @staticmethod
    def get_all(db: Session, status: str = "", keyword: str = ""):
        """获取意向客户列表"""
        query = db.query(CrmLead)
        if status:
            query = query.filter(CrmLead.status == status)
        if keyword:
            query = query.filter(CrmLead.customer_name.contains(keyword))
        return query.order_by(CrmLead.create_time.desc()).limit(50).all()

    @staticmethod
    def get_by_id(db: Session, lead_id: int):
        """根据ID获取客户"""
        return db.query(CrmLead).filter(CrmLead.id == lead_id).first()

    @staticmethod
    def create(db: Session, customer_name: str, contact_info: str, background_info: str, status: str, owner_employee_id: int):
        """新增意向客户"""
        lead = CrmLead(
            customer_name=customer_name,
            contact_info=contact_info,
            background_info=background_info,
            status=status,
            owner_employee_id=owner_employee_id
        )
        db.add(lead)
        return lead

    @staticmethod
    def update_status(db: Session, lead_id: int, status: str = None, follow_up_history: str = None):
        """更新客户状态或跟进记录"""
        lead = db.query(CrmLead).filter(CrmLead.id == lead_id).first()
        if lead:
            if status:
                lead.status = status
            if follow_up_history:
                history = lead.follow_up_history or ""
                lead.follow_up_history = history + f"\n[{datetime.now().strftime('%Y-%m-%d')}] {follow_up_history}"
        return lead


class ReportDAO:
    """日报数据访问对象"""

    @staticmethod
    def create(db: Session, employee_id: int, content: str, report_date: str):
        """提交日报"""
        report = EmployeeDailyReport(
            employee_id=employee_id,
            content=content,
            report_date=report_date
        )
        db.add(report)
        return report

    @staticmethod
    def get_all(db: Session, date: str = "", employee_id: int = 0):
        """查询日报"""
        query = db.query(EmployeeDailyReport)
        if date:
            query = query.filter(EmployeeDailyReport.report_date == date)
        if employee_id:
            query = query.filter(EmployeeDailyReport.employee_id == employee_id)
        return query.order_by(EmployeeDailyReport.create_time.desc()).limit(30).all()


class ScoreDAO:
    """成绩数据访问对象"""

    @staticmethod
    def create(db: Session, student_id: int, course_name: str, score: float, semester: str):
        """录入成绩"""
        record = StudentScore(
            student_id=student_id,
            course_name=course_name,
            score=score,
            semester=semester
        )
        db.add(record)
        return record

    @staticmethod
    def get_all(db: Session, student_id: int = 0):
        """查询成绩"""
        query = db.query(StudentScore)
        if student_id:
            query = query.filter(StudentScore.student_id == student_id)
        return query.order_by(StudentScore.create_time.desc()).all()


class StudentServiceDAO:
    """学生行政服务数据访问对象"""

    @staticmethod
    def create_leave(db: Session, student_id: int, service_type: str, start_time: datetime, end_time: datetime, reason: str):
        """提交请假申请"""
        leave = StudentAdminService(
            student_id=student_id,
            service_type=service_type,
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
        query = db.query(StudentAdminService).filter(StudentAdminService.service_type == "请假")
        if student_id:
            query = query.filter(StudentAdminService.student_id == student_id)
        return query.order_by(StudentAdminService.create_time.desc()).all()


class FeedbackDAO:
    """投诉反馈数据访问对象"""

    @staticmethod
    def create(db: Session, student_id: int, content: str, detail: str):
        """提交投诉反馈"""
        ticket = StudentFeedbackTicket(
            student_id=student_id,
            content=content,
            detail=detail,
            status="待处理"
        )
        db.add(ticket)
        return ticket

    @staticmethod
    def get_all(db: Session, student_id: int = 0):
        """查询投诉反馈"""
        query = db.query(StudentFeedbackTicket)
        if student_id:
            query = query.filter(StudentFeedbackTicket.student_id == student_id)
        return query.order_by(StudentFeedbackTicket.create_time.desc()).all()


class PsychAlertDAO:
    """心理预警数据访问对象"""

    @staticmethod
    def create(db: Session, student_id: int, trigger_reason: str, risk_level: str):
        """提交心理预警"""
        alert = StudentPsychAlert(
            student_id=student_id,
            trigger_reason=trigger_reason,
            risk_level=risk_level,
            status="未处理"
        )
        db.add(alert)
        return alert

    @staticmethod
    def get_all(db: Session, risk_level: str = ""):
        """查询心理预警"""
        query = db.query(StudentPsychAlert)
        if risk_level:
            query = query.filter(StudentPsychAlert.risk_level == risk_level)
        return query.order_by(StudentPsychAlert.create_time.desc()).all()

    @staticmethod
    def update_profile(db: Session, student_id: int, risk_level: str):
        """更新心理画像"""
        profile = db.query(StudentPsychProfile).filter(
            StudentPsychProfile.student_id == student_id
        ).first()

        if profile:
            profile.latest_emotion_tag = risk_level
            profile.emotion_score = 20 if risk_level == "高" else (40 if risk_level == "中" else 60)
        else:
            new_profile = StudentPsychProfile(
                student_id=student_id,
                latest_emotion_tag=risk_level,
                emotion_score=20 if risk_level == "高" else 40,
                last_interaction_time=datetime.now()
            )
            db.add(new_profile)


class DashboardDAO:
    """仪表盘数据访问对象"""

    @staticmethod
    def get_stats(db: Session):
        """获取统计数据"""
        # 客户统计
        total_leads = db.query(CrmLead).count()
        status_counts = {}
        for s in ["新增意向", "跟进中", "已签约", "已流失"]:
            status_counts[s] = db.query(CrmLead).filter(CrmLead.status == s).count()

        # 投诉统计
        total_tickets = db.query(StudentFeedbackTicket).count()
        pending_tickets = db.query(StudentFeedbackTicket).filter(
            StudentFeedbackTicket.status == "待处理"
        ).count()

        # 心理预警统计
        high_risk = db.query(StudentPsychAlert).filter(StudentPsychAlert.risk_level == "高").count()
        medium_risk = db.query(StudentPsychAlert).filter(StudentPsychAlert.risk_level == "中").count()

        # 日报统计
        today = datetime.now().strftime("%Y-%m-%d")
        today_reports = db.query(EmployeeDailyReport).filter(
            EmployeeDailyReport.report_date == today
        ).count()

        return {
            "customers": {"total": total_leads, "by_status": status_counts},
            "feedback": {"total": total_tickets, "pending": pending_tickets},
            "psych_alerts": {"high": high_risk, "medium": medium_risk},
            "daily_reports": {"today": today_reports}
        }
