import enum
import random
from datetime import datetime, timedelta

import ujson
from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("sqlite:///database.sqlite3")
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)


class SiteEnum(enum.Enum):
    olx = "OLX"
    mercado_livre = "Mercado Livre"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    site = Column(Enum(SiteEnum))
    email = Column(String)
    password = Column(String)
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


def get_accounts():
    session = Session()

    return session.query(Account).all()


def add_account(site: str, email: str, password: str):
    session = Session()
    account = Account(site=SiteEnum(site), email=email, password=password)
    session.add(account)
    session.commit()
    session.close()


def edit_account(account: Account, email: str, password: str):
    session = Session()
    account.email = email
    account.password = password
    session.commit()


def delete_account(account: Account):
    session = Session()
    session.delete(account)
    session.commit()


def add_tasks(site: str, info: dict, titles: list, descriptions: list, interval: int):
    session = Session()

    site = SiteEnum(site)

    tasks = []

    c = 0
    for account in session.query(Account).all():
        this_info = ujson.loads(info)
        this_info["input_subject"] = random.choice(titles)
        this_info["input_body"] = random.choice(descriptions)
        task_datetime = datetime.now() + timedelta(minutes=interval * c + 1)
        tasks.append(
            Task(
                site=SiteEnum(site),
                datetime=task_datetime,
                account=account,
                info=ujson.dumps(this_info)
            )
        )
        c += 1

    session.add_all(tasks)
    session.commit()

    return tasks
