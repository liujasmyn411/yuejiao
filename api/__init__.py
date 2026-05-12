"""
粤教服务 - API路由层
处理HTTP请求和响应，调用DAO层完成业务逻辑
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from schemas import (
    EventRegisterRequest, LeadCreateRequest, LeadUpdateRequest,
    ReportCreateRequest, ScoreCreateRequest, LeaveCreateRequest,
    FeedbackCreateRequest, PsychAlertCreateRequest
)
from dao import (
    EventDAO, ProjectDAO, CrmDAO, ReportDAO, ScoreDAO,
    StudentServiceDAO, FeedbackDAO, PsychAlertDAO, DashboardDAO
)


# ========== 路由定义 ==========

router = APIRouter()


# ---------- 根路径 ----------
@router.get("/")
def root():
    return {"msg": "粤教服务AI Agent API运行中", "status": "ok"}


# ---------- 健康检查 ----------
@router.get("/health")
def health_check():
    return {"status": "healthy", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# ==================== 客服Agent接口 ====================

# ---- 活动列表 ----
@router.get("/api/events")
def list_events(db: Session = Depends(get_db)):
    """获取所有活动列表"""
    events = EventDAO.get_all(db)
    result = []
    for e in events:
        remaining = (e.max_participants or 0) - (e.current_participants or 0)
        result.append({
            "id": e.id,
            "event_name": e.event_name,
            "event_type": e.event_type,
            "start_time": e.start_time.strftime("%Y-%m-%d %H:%M") if e.start_time else "",
            "location": e.location,
            "max_participants": e.max_participants,
            "current_participants": e.current_participants,
            "remaining_slots": remaining,
            "status": "即将满员" if remaining < 5 else "开放报名"
        })
    return {"events": result, "total": len(result)}


# ---- 即将开始的活动 ----
@router.get("/api/events/upcoming")
def upcoming_events(limit: int = 5, db: Session = Depends(get_db)):
    """获取即将开始的活动"""
    events = EventDAO.get_upcoming(db, limit)
    result = []
    for e in events:
        remaining = (e.max_participants or 0) - (e.current_participants or 0)
        result.append({
            "id": e.id,
            "event_name": e.event_name,
            "event_type": e.event_type,
            "start_time": e.start_time.strftime("%Y-%m-%d %H:%M") if e.start_time else "",
            "location": e.location,
            "remaining_slots": remaining,
            "status": "即将满员" if remaining < 5 else "开放报名"
        })
    return {"events": result, "total": len(result)}


# ---- 活动详情 ----
@router.get("/api/events/{event_id}")
def event_detail(event_id: int, db: Session = Depends(get_db)):
    """获取单个活动详情"""
    e = EventDAO.get_by_id(db, event_id)
    if not e:
        raise HTTPException(status_code=404, detail="活动不存在")

    remaining = (e.max_participants or 0) - (e.current_participants or 0)
    return {
        "id": e.id,
        "event_name": e.event_name,
        "event_type": e.event_type,
        "start_time": e.start_time.strftime("%Y-%m-%d %H:%M") if e.start_time else "",
        "location": e.location,
        "max_participants": e.max_participants,
        "current_participants": e.current_participants,
        "remaining_slots": remaining
    }


# ---- 活动报名 ----
@router.post("/api/events/register")
def register_event(req: EventRegisterRequest, db: Session = Depends(get_db)):
    """活动报名"""
    event = EventDAO.get_by_id(db, req.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="活动不存在")

    remaining = (event.max_participants or 0) - (event.current_participants or 0)
    if remaining <= 0:
        raise HTTPException(status_code=400, detail="活动已满员")

    EventDAO.create_registration(db, req.event_id, req.customer_name, req.customer_phone)
    EventDAO.increment_participants(db, req.event_id)
    db.commit()

    return {
        "success": True,
        "message": f"【{req.customer_name}】报名成功！",
        "event_name": event.event_name,
        "start_time": event.start_time.strftime("%Y-%m-%d %H:%M") if event.start_time else "",
        "location": event.location,
        "remaining_slots": remaining - 1
    }


# ---- 项目列表 ----
@router.get("/api/projects")
def list_projects(category: str = "", db: Session = Depends(get_db)):
    """获取项目列表"""
    projects = ProjectDAO.get_all(db, category)
    return {
        "projects": [
            {
                "id": p.id,
                "project_name": p.project_name,
                "category": p.category,
                "description": p.description,
                "target_audience": p.target_audience
            }
            for p in projects
        ]
    }


# ==================== 企业助手接口 ====================

# ---- CRM: 意向客户列表 ----
@router.get("/api/crm/leads")
def list_leads(status: str = "", keyword: str = "", db: Session = Depends(get_db)):
    """查询意向客户列表"""
    leads = CrmDAO.get_all(db, status, keyword)
    return {
        "leads": [
            {
                "id": l.id,
                "customer_name": l.customer_name,
                "contact_info": l.contact_info,
                "background_info": l.background_info,
                "status": l.status,
                "follow_up_history": l.follow_up_history,
                "create_time": l.create_time.strftime("%Y-%m-%d %H:%M") if l.create_time else ""
            }
            for l in leads
        ]
    }


# ---- CRM: 新增意向客户 ----
@router.post("/api/crm/leads")
def create_lead(req: LeadCreateRequest, db: Session = Depends(get_db)):
    """新增意向客户"""
    lead = CrmDAO.create(db, req.customer_name, req.contact_info, req.background_info, req.status, req.owner_employee_id)
    db.commit()
    db.refresh(lead)
    return {"success": True, "lead_id": lead.id, "message": f"客户【{req.customer_name}】录入成功"}


# ---- CRM: 更新客户状态 ----
@router.put("/api/crm/leads/{lead_id}")
def update_lead(lead_id: int, req: LeadUpdateRequest, db: Session = Depends(get_db)):
    """更新意向客户状态或跟进记录"""
    lead = CrmDAO.get_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="客户不存在")

    CrmDAO.update_status(db, lead_id, req.status, req.follow_up_history)
    db.commit()
    return {"success": True, "message": f"客户【{lead.customer_name}】更新成功", "status": lead.status}


# ---- 日报: 提交 ----
@router.post("/api/reports/daily")
def create_report(req: ReportCreateRequest, db: Session = Depends(get_db)):
    """提交日报"""
    ReportDAO.create(db, req.employee_id, req.content, req.report_date)
    db.commit()
    return {"success": True, "message": "日报提交成功"}


# ---- 日报: 查询 ----
@router.get("/api/reports/daily")
def list_reports(date: str = "", employee_id: int = 0, db: Session = Depends(get_db)):
    """查询日报"""
    reports = ReportDAO.get_all(db, date, employee_id)
    return {
        "reports": [
            {
                "id": r.id,
                "employee_id": r.employee_id,
                "report_date": r.report_date,
                "content": r.content,
                "create_time": r.create_time.strftime("%Y-%m-%d %H:%M") if r.create_time else ""
            }
            for r in reports
        ]
    }


# ---- 成绩: 录入 ----
@router.post("/api/scores")
def create_score(req: ScoreCreateRequest, db: Session = Depends(get_db)):
    """录入学生成绩"""
    ScoreDAO.create(db, req.student_id, req.course_name, req.score, req.semester)
    db.commit()
    return {"success": True, "message": "成绩录入成功"}


# ---- 成绩: 查询 ----
@router.get("/api/scores")
def list_scores(student_id: int = 0, db: Session = Depends(get_db)):
    """查询学生成绩"""
    scores = ScoreDAO.get_all(db, student_id)
    return {
        "scores": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "course_name": s.course_name,
                "score": s.score,
                "semester": s.semester
            }
            for s in scores
        ]
    }


# ==================== 学生助手接口 ====================

# ---- 请假: 提交 ----
@router.post("/api/student/leave")
def create_leave(req: LeaveCreateRequest, db: Session = Depends(get_db)):
    """学生提交请假申请"""
    StudentServiceDAO.create_leave(
        db, req.student_id, req.service_type,
        datetime.strptime(req.start_time, "%Y-%m-%d %H:%M"),
        datetime.strptime(req.end_time, "%Y-%m-%d %H:%M"),
        req.reason
    )
    db.commit()
    return {"success": True, "message": "请假申请已提交，等待审批"}


# ---- 请假: 查询 ----
@router.get("/api/student/leave")
def list_leaves(student_id: int = 0, db: Session = Depends(get_db)):
    """查询请假记录"""
    leaves = StudentServiceDAO.get_leaves(db, student_id)
    return {"leaves": [
        {"id": l.id, "student_id": l.student_id, "start": str(l.start_time),
         "end": str(l.end_time), "reason": l.reason, "status": l.status}
        for l in leaves
    ]}


# ---- 投诉反馈: 提交 ----
@router.post("/api/student/feedback")
def create_feedback(req: FeedbackCreateRequest, db: Session = Depends(get_db)):
    """学生提交投诉反馈"""
    ticket = FeedbackDAO.create(db, req.student_id, req.content, req.detail)
    db.commit()
    return {"success": True, "ticket_id": ticket.id, "message": "投诉已提交，我们会尽快处理"}


# ---- 投诉反馈: 查询 ----
@router.get("/api/student/feedback")
def list_feedback(student_id: int = 0, db: Session = Depends(get_db)):
    """查询投诉反馈列表"""
    tickets = FeedbackDAO.get_all(db, student_id)
    return {"tickets": [
        {"id": t.id, "student_id": t.student_id, "content": t.content,
         "status": t.status, "solution": t.solution}
        for t in tickets
    ]}


# ---- 心理预警: 提交 ----
@router.post("/api/student/psych-alert")
def create_psych_alert(req: PsychAlertCreateRequest, db: Session = Depends(get_db)):
    """提交心理预警"""
    alert = PsychAlertDAO.create(db, req.student_id, req.trigger_reason, req.risk_level)
    PsychAlertDAO.update_profile(db, req.student_id, req.risk_level)
    db.commit()
    return {"success": True, "alert_id": alert.id,
            "message": f"⚠️ 已记录{req.risk_level}风险预警，老师会尽快跟进"}


# ---- 心理预警: 查询 ----
@router.get("/api/student/psych-alert")
def list_psych_alerts(risk_level: str = "", db: Session = Depends(get_db)):
    """查询心理预警列表"""
    alerts = PsychAlertDAO.get_all(db, risk_level)
    return {"alerts": [
        {"id": a.id, "student_id": a.student_id, "trigger_reason": a.trigger_reason,
         "risk_level": a.risk_level, "status": a.status}
        for a in alerts
    ]}


# ==================== 智能报告接口 ====================

@router.get("/api/reports/dashboard")
def dashboard(db: Session = Depends(get_db)):
    """管理仪表盘数据"""
    return DashboardDAO.get_stats(db)
