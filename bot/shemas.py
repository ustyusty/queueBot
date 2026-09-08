from pydantic import BaseModel, Field
from datetime import datetime
class CourseShema(BaseModel):
    title: str = Field(..., min_length=1)

class GroupShema(BaseModel):
    title: str = Field(..., min_length=1)

class UserShema(BaseModel):
    telegramId: int
    username: str | None
    nicname: str
    is_admin: bool = False

class QueuePiceShema(BaseModel):
    user: UserShema
    course: CourseShema
    group: GroupShema
    is_pass: bool = False
    register_at: datetime
    close_at: datetime | None

    
