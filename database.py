from datetime import datetime, timedelta
import enum

from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("sqlite:///:memory:")
Base = declarative_base()
Session = sessionmaker(bind=engine)


class SiteEnum(enum.Enum):
    olx = "OLX"
    mercado_livre = "Mercado Livre"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    account_site = Column(Enum(SiteEnum))
    email = Column(String)
    password = Column(String)
    zipcode = Column(Integer)
    tasks = relationship("Task", back_populates="account")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    site = Column(Enum(SiteEnum))
    datetime = Column(DateTime)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="tasks")
    info = Column(String)


def create_all():
    Base.metadata.create_all(engine)


def get_pendent_tasks():
    session = Session()

    return session.query(Task).filter(Task.datetime > datetime.now()).all()


def add_account():
    pass


def add_tasks(site: str, info):
    session = Session()

    site = SiteEnum(site)

    tasks = []

    c = 1
    for account in session.query(Account).all():
        task_datetime = datetime.now() + timedelta(hours=c)
        tasks.append(
            Task(
                site=site,
                datetime=task_datetime,
                account=account,
                info=info
            )
        )
        c += 1

    session.add_all(tasks)
    session.commit()

    return tasks
