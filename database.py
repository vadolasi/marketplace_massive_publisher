import random
from datetime import datetime, timedelta
from sqlalchemy.sql.sqltypes import Boolean

import ujson
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, desc
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("sqlite:///database.sqlite3")
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    tasks = relationship("Task", back_populates="account")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="tasks")
    info = Column(String)
    success = Column(Boolean)


def create_all():
    Base.metadata.create_all(engine)


def get_pendent_tasks():
    session = Session()

    tasks = session.query(Task).filter(Task.datetime > datetime.now())
    session.close()

    return tasks


def get_accounts():
    session = Session()

    accounts =  session.query(Account).all()
    session.close()

    return accounts


def get_account(account_id: int):
    session = Session()

    account = session.query(Account).get(account_id)
    session.close()

    return account


def add_account(email: str, password: str):
    session = Session()
    account = Account(email=email, password=password)
    session.add(account)
    session.commit()
    session.close()

    return account


def edit_account(account: Account, email: str, password: str):
    session = Session()
    account.email = email
    account.password = password
    session.commit()
    session.close()


def delete_account(account: Account):
    session = Session()
    session.delete(account)
    session.commit()
    session.close()


def add_tasks(info: dict, titles: list, descriptions: list, images: list, interval: int):
    session = Session()

    tasks = []

    c = 0
    for account in session.query(Account).all():
        this_info = ujson.loads(info)
        this_info["input_subject"] = random.choice(titles)
        this_info["input_body"] = random.choice(descriptions)
        this_info["images"] = images
        task_datetime = datetime.now() + timedelta(minutes=interval * c + 1)
        tasks.append(
            Task(
                datetime=task_datetime,
                account=account,
                info=ujson.dumps(this_info)
            )
        )
        c += 1

    session.add_all(tasks)
    session.commit()
    session.close()

    return tasks


def get_task(task_id: int):
    session = Session()
    task = session.query(Task).get(task_id)
    session.close()

    return task


def get_tasks():
    session = Session()
    tasks = session.query(Task).filter(Task.datetime <= datetime.now()).order_by(desc(Task.datetime))
    session.close()

    return tasks


def complete_task(task: Task, success: bool):
    session = Session()
    task.success = success
    session.commit()
    session.close()
