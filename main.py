import questionary

import database
import tasks
import web_automation

database.create_all()

for task in database.get_pendent_tasks():
    tasks.add_task(task)

action = questionary.select(
    "O que você deseja fazer?",
    choices=["Gerenciar contas", "Publicar em massa"],
).ask()

if action == "Gerenciar contas":
    pass
else:
    site = questionary.select(
        "Onde deseja publicar?",
        choices=["OLX", "Mercado Livre"],
    ).ask()

    if site == "OLX":
        web_automation.olx()
    else:
        pass
