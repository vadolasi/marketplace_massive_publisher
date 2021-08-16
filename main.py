import questionary
from rich.console import Console

import database
import tasks
import web_automation


console = Console()
database.create_all()

for task in database.get_pendent_tasks():
    tasks.add_task(task)

while True:
    action = questionary.select(
        "O que você deseja fazer?",
        choices=["Gerenciar contas", "Publicar em massa", "Sair"],
    ).ask()

    if action == "Gerenciar contas":
        site = questionary.select(
            "Deseja gerenciar as contas de qual site?",
            choices=["OLX", "Mercado Livre"],
        ).ask()

        subaction = questionary.select(
            "O que você deseja fazer?",
            choices=["Adicionar contas", "Ver contas"]
        ).ask()

        if subaction == "Adicionar contas":    
            continue_add_accounts = True

            while continue_add_accounts:
                email = questionary.text("Informe o email da conta").ask()
                password = questionary.text("Informe a senha da conta").ask()

                database.add_account(site, email, password)

                continue_add_accounts = questionary.confirm(f"Conta adiciona com sucesso! Deseja adicionar outra conta no {site}?").ask()
        else:
            accounts = database.get_accounts()
            accounts_emails = [account.email for account in database.get_accounts()]

            if accounts_emails:
                account = questionary.select(
                    "Lista de contas, selecione uma conta para gerencia-la, ou ctrl + c para sair",
                    choices=accounts_emails
                ).ask()

                account = accounts[accounts_emails.index(account)]

                if account:
                    subsubaction = questionary.select(
                        f"Email: {account.email} / Senha: {account.password} / O que você deseja fazer?",
                        choices=["Sair", "Editar", "Deletar"]
                    ).ask()

                    if subsubaction == "Editar":
                        email = questionary.text(
                            "Informe o novo email (ou deixe em branco para manter o atual)"
                        ).ask()
                        password = questionary.text(
                            "Informe o novo email (ou deixe em branco para manter o atual)"
                        ).ask()
                        if not email:
                            email = account.email
                        if not password:
                            password = account.password

                        database.edit_account(account, email, password)
                        console.print("\nConta editada com sucesso!\n")

                    elif subsubaction == "Deletar":
                        if questionary.confirm("Deseja mesmo deletar essa conta").ask():
                            database.delete_account(account)

                            console.print("\nConta deletada com sucesso!\n")

            else:
                console.print("\nVocê ainda não criou nenhuma conta!\n")

    elif action == "Publicar em massa":
        site = questionary.select(
            "Onde deseja publicar?",
            choices=["OLX", "Mercado Livre"],
        ).ask()

        if site == "OLX":
            web_automation.olx()
        else:
            pass

    else:
        break
