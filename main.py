import tkinter as tk
from functools import partial
from tkinter import ttk, messagebox, filedialog

import ujson

import database
import tasks
import web_automation

database.create_all()

for task in database.get_pendent_tasks():
    tasks.add_task(task)


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class ScreenManager():
    def __init__(self):
        self.screens = {}
        self.current_screen = None

    def add_screen(self, screen: "Screen"):
        self.screens[screen.name] = screen

        if not self.current_screen:
            self.current_screen = screen
            self.current_screen.pack()
        
    def open_screen(self, screen_name: str, *args, **kwargs):
        return partial(self._open_screen, screen_name, *args, **kwargs)

    def _open_screen(self, screen_name: str, *args, **kwargs):
        self.current_screen.pack_forget()
        self.current_screen = self.screens[screen_name]
        self.current_screen.refresh(*args, **kwargs)
        self.current_screen.pack()


class Screen(tk.Frame):
    def __init__(self, screen_manager: "ScreenManager", name: str, root):
        super().__init__(root)
        self.name = name
        self.screen_manager = screen_manager

        self.screen_manager.add_screen(self)
    
    def refresh(self, *args, **kwargs):
        pass


class HomeScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tk.Button(
            self,
            text="Gerenciar contas",
            command=self.screen_manager.open_screen("manage_accounts")
        ).pack()
        tk.Button(
            self,
            text="Publicar em massa",
            command=self.create_task
        ).pack()
        tk.Button(
            self,
            text="Ver histórico de publicações",
            command=self.screen_manager.open_screen("tasks_history")
        ).pack()

    def create_task(self):
        structure = web_automation.create_task()

        if structure:
            self.screen_manager.open_screen("add_info", structure)()
        else:
            messagebox.showerror("Erro", "Você precisa inserir uma conta para prosseguir")


class AddInfoScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.structure = None

        self.images = []

        tk.Label(self, text="Informe as opções de títulos (separados por linha)").pack()
        self.titles_input = tk.Text(self, height=5)
        self.titles_input.pack()
        tk.Label(self, text="Informe as opções de descrições (separados por \"---\")").pack()
        self.descriptions_input = tk.Text(self, height=5)
        self.descriptions_input.pack()
        tk.Button(self, text="Selecione as imagens", command=self.select_images).pack()
        interval_frame = tk.Frame(self)
        interval_frame.pack()
        tk.Label(interval_frame, text="Informe o intervalo entre cada publicação").grid(row=0, column=0)

        def MoneyValidation(S):
            if S in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:

                return True

            self.bell()
    
            return False

        vcmd = (self.register(MoneyValidation), "%S")
        self.interval_input = tk.Entry(interval_frame, validate="key", vcmd=vcmd)
        self.interval_input.grid(row=0, column=1)
        tk.Button(self, text="Concluir", command=self.complete).pack()

    def select_images(self):
        filetypes = (
            ("Imagens", "*.gif *.jpg *.jpeg *.png"),
            ("Todos os arquivos", "*.*")
        )
        self.images = filedialog.askopenfilenames(filetypes=filetypes)

    def complete(self):
        titles = self.titles_input.get("1.0", tk.END)[:-2].split("\n")
        descriptions = self.descriptions_input.get("1.0", tk.END)[:-2].split("\n---\n")

        tasks_list = database.add_tasks(
            ujson.dumps(self.structure),
            titles,
            descriptions,
            self.images,
            int(self.interval_input.get())
        )

        for task in tasks_list:
            tasks.add_task(task)

        self.screen_manager.open_screen("home")()

    def refresh(self, structure):
        self.structure = structure


class ManageAccountsScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.accounts_table = ttk.Treeview(self, columns=["Email", "Senha"])
        self.accounts_table.pack(fill=tk.BOTH, expand=True)
        self.accounts_table.column("#0", width=0, stretch=tk.NO)
        self.accounts_table.column("Email", width=250)
        self.accounts_table.column("Senha", width=250)
        self.accounts_table.heading("#0", text="", anchor=tk.W)
        self.accounts_table.heading("Email", text="Email", anchor=tk.W)
        self.accounts_table.heading("Senha", text="Senha", anchor=tk.W)

        self.accounts_index = 0
        for account in database.get_accounts():
            self.accounts_table.insert(
                parent="",
                index=self.accounts_index,
                iid=account.id,
                text=account.id,
                values=(account.email, account.password)
            )
            self.accounts_index += 1

        add_row = tk.Frame(self)
        add_row.pack()

        tk.Label(add_row, text="Email").grid(column=0, row=0)
        self.email_input = tk.Entry(add_row, width=23)
        self.email_input.grid(column=0, row=1)
        tk.Label(add_row, text="Senha").grid(column=1, row=0)
        self.password_input = tk.Entry(add_row, width=23)
        self.password_input.grid(column=1, row=1)
        tk.Button(
            add_row,
            text="Adicionar",
            command=self.add
        ).grid(column=2, row=1)
        tk.Button(
            add_row,
            text="Voltar",
            command=self.screen_manager.open_screen("home")
        ).grid(column=0, row=2)
        tk.Button(
            add_row,
            text="Deletar",
            command=self.delete
        ).grid(column=2, row=2)

    def add(self):
        email = self.email_input.get()
        self.email_input.delete(0, "end")
        password = self.password_input.get()
        self.password_input.delete(0, "end")

        account = database.add_account(email, password)

        self.accounts_index += 1
        self.accounts_table.insert(
            parent="",
            index=self.accounts_index,
            iid=account.id,
            text=account.id,
            values=(account.email, account.password)
        )

    def delete(self):
        account_item = self.accounts_table.focus()
        account_item_id = self.accounts_table.item(account_item)["text"]

        database.delete_account(
            database.get_account(int(account_item_id))
        )

        self.accounts_table.delete(account_item)


class PublicationsHistory(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tasks_list = tk.Listbox(self)
        self.tasks_list.pack()

        for index, task in enumerate(database.get_tasks()):
            self.tasks_list.insert(index, f"{ujson.loads(task.info)['input_subject']} {task.id}")

        tk.Button(
            self,
            text="Ver publicação",
            command=self.open_task
        ).pack()
        tk.Button(
            self,
            text="Voltar",
            command=self.screen_manager.open_screen("home")
        ).pack()
    
    def open_task(self):
        task_id = int(self.tasks_list.get(tk.ANCHOR).split()[-1])
        self.screen_manager.open_screen("publication_info", task_id)()

    def refresh(self, *args, **kwargs):
        self.tasks_list.delete(0, tk.END)

        for index, task in enumerate(database.get_tasks()):
            self.tasks_list.insert(index, f"{ujson.loads(task.info)['input_subject']} {task.id}")


class PublicationInfo(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title_text = tk.Label(self)
        self.title_text.pack()
        self.description_text = tk.Label(self)
        self.description_text.pack()
        self.datetime_text = tk.Label(self)
        self.datetime_text.pack()
        self.success_text = tk.Label(self)
        self.success_text.pack()
        tk.Button(
            self,
            text="Voltar",
            command=self.screen_manager.open_screen("home")
        ).pack()

    def refresh(self, task_id: int):
        task = database.get_task(task_id)
        task_info = ujson.loads(task.info)
        self.title_text.config(text=f"Título: {task_info['input_subject']}")
        self.description_text.config(text=f"Descrição: {task_info['input_body']}")
        self.datetime_text.config(
            text=f"Data e hora: {task.datetime.day}/{task.datetime.month}/{task.datetime.year}"
            f" às {task.datetime.hour}:{task.datetime.minute}"
        )
        if task.success:
            self.success_text.config(text="A publicação foi feita com sucesso")
        else:
            self.success_text.config(text="A publicação não ocorreu com sucesso")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.resizable(False, False)    
        self.geometry("500x310")
        self.title("Publicador em massa")

        screen_manager = ScreenManager()
        HomeScreen(screen_manager, "home", self)
        ManageAccountsScreen(screen_manager, "manage_accounts", self)
        PublicationsHistory(screen_manager, "tasks_history", self)
        AddInfoScreen(screen_manager, "add_info", self)
        PublicationInfo(screen_manager, "publication_info", self)


app = App()
app.mainloop()
