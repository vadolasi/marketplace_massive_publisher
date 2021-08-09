import questionary

import database
import tasks
import web_automation

database.create_all()

for task in database.get_pendent_tasks():
    tasks.add_task(task)

while True:
    action = questionary.select(
        "O que você deseja fazer?",
        choices=["Adicionar contas", "Publicar em massa"],
    ).ask()

    if action == "Adicionar contas":
        site = questionary.select(
            "Deseja gerenciar as contas de qual site?",
            choices=["OLX", "Mercado Livre"],
        ).ask()

        continue_add_accounts = True

        while continue_add_accounts:
            email = questionary.text("Informe o email da conta").ask()
            password = questionary.text("Informe a senha da conta").ask()

            database.add_account(site, email, password)

            continue_add_accounts = questionary.confirm(f"Conta adiciona com sucesso! Deseja adicionar outra conta no {site}?").ask()

    else:
        site = questionary.select(
            "Onde deseja publicar?",
            choices=["OLX", "Mercado Livre"],
        ).ask()

        if site == "OLX":
            web_automation.olx()
        else:
            pass
