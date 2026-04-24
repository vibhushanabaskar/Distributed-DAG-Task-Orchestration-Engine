from sqlalchemy import Column, String, Text, ForeignKey, JSON, Integer, DateTime
from sqlalchemy.orm import relationship
from core.db.database import Base
from datetime import datetime

class DAG(Base):
    __tablename__ = "dags"

    id = Column(String, primary_key=True)

    tasks = relationship(
        "Task",
        back_populates="dag",
        cascade="all, delete"
    )

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    command = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)  # newly added
    status = Column(String, default="PENDING")
    dependencies = Column(JSON, default=[])
    dag_id = Column(String, ForeignKey("dags.id", ondelete="CASCADE"))
    dag = relationship("DAG", back_populates="tasks")


class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(
        String,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True
    )

    log_content = Column(Text, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task")
