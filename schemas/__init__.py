"""
粤教服务 - API请求/响应模型
定义所有Pydantic数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional


# ---- 活动相关 ----
class EventRegisterRequest(BaseModel):
    event_id: int
    customer_name: str
    customer_phone: str = ""


# ---- CRM意向客户相关 ----
class LeadCreateRequest(BaseModel):
    customer_name: str
    contact_info: str = ""
    background_info: str = ""
    status: str = "新增意向"
    owner_employee_id: int = 1


class LeadUpdateRequest(BaseModel):
    status: Optional[str] = None
    follow_up_history: Optional[str] = None


# ---- 日报相关 ----
class ReportCreateRequest(BaseModel):
    employee_id: int
    content: str
    report_date: str = Field(default_factory=lambda: __import__('datetime').datetime.now().strftime("%Y-%m-%d"))


# ---- 学生成绩相关 ----
class ScoreCreateRequest(BaseModel):
    student_id: int
    course_name: str
    score: float
    semester: str = ""


# ---- 请假相关 ----
class LeaveCreateRequest(BaseModel):
    student_id: int
    service_type: str = "请假"
    start_time: str
    end_time: str
    reason: str = ""


# ---- 投诉反馈相关 ----
class FeedbackCreateRequest(BaseModel):
    student_id: int
    content: str
    detail: str = ""


# ---- 心理预警相关 ----
class PsychAlertCreateRequest(BaseModel):
    student_id: int
    trigger_reason: str
    risk_level: str  # 高 / 中 / 低
