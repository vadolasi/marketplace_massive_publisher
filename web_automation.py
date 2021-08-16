import random
import time

import questionary
import ujson
from rich.console import Console
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

import database
import tasks

console = Console()


def send_keys(input_, keys):
    for key in keys:
        input_.send_keys(key)
        time.sleep(random.random())


def olx():
    for account in database.get_accounts():
        try:
            driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
            driver.implicitly_wait(30)

            console.print(
                "\n[bold]Foi aberto um navegador, que ira entrar automaticamente na pagina "
                "de publicar anuncio no OLX. Coloque todas as informações e depois "
                "aperte enter[/bold]"
            )

            driver.get("https://olx.com.br/")
            time.sleep(random.random())
            driver.find_element_by_css_selector("a.sc-jAaTju.gshyPU").click()

            inputs = driver.find_elements_by_css_selector("input.sc-dEoRIm.drdMJh")
            time.sleep(random.random())
            send_keys(inputs[0], account.email)
            time.sleep(random.random())
            send_keys(inputs[1], account.password)
            time.sleep(random.random())
            driver.find_element_by_css_selector("button.sc-kGXeez.kgGtxX").click()

            input()

            structure = {}

            inputs = driver.find_elements_by_xpath("//form[@id='aiform']//input")
            textareas = driver.find_elements_by_xpath("//form[@id='aiform']//textarea")
            selects = driver.find_elements_by_xpath("//form[@id='aiform']//select")

            for input_ in inputs:
                input_type = input_.get_attribute("type")
                input_id = input_.get_attribute("id")

                if input_type == "text" or input_type == "hidden":
                    structure[input_id] = input_.get_attribute("value")
                elif input_type == "checkbox" or input_type == "radio":
                    structure[input_id] = input_.is_selected()

            for textarea in textareas:
                structure[textarea.get_attribute("id")] = input_.get_attribute("value")

            for select in selects:
                select_id = select.get_attribute("id")
                select = Select(select)
                structure[select_id] = select.first_selected_option.text

            driver.quit()

            titles = []
            descriptions = []

            titles.append(questionary.text("Informe um título para o anuncio").ask())

            while True:
                title = questionary.text("Informe outro título (ou aperte enter para continuar)").ask()
                if title:
                    titles.append(title)
                else:
                    break

            descriptions.append(questionary.text("Informe uma descrição para o anuncio").ask())

            while True:
                description = questionary.text("Informe outra descrição (ou aperte enter para continuar)").ask()
                if description:
                    descriptions.append(description)
                else:
                    break

            interval = questionary.text("Informe o tempo (em minutos) entre cada anuncio").ask()

            while not isinstance(interval, int):
                try:
                    interval = int(interval)
                except:
                    interval = questionary.text("Informe um valor válido!").ask()

            for task in database.add_tasks("OLX", ujson.dumps(structure), titles, descriptions, interval):
                tasks.add_task(task)

            console.print(
                f"\n[bold]Ação realizada com sucesso! Cada anuncio será publicado a cada {interval} minutos."
                " As publicações só serão realizadas caso esse programa esteja sendo executado[/bold]\n"
            )

            break

        except Exception as exception:
            print(exception)


def run_olx_task(task):
    try:
        options = Options()
        # options.add_argument("--headless")

        driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=options)
        driver.implicitly_wait(2)

        driver.get("https://olx.com.br/")
        time.sleep(random.random())
        driver.find_element_by_css_selector("a.sc-jAaTju.gshyPU").click()

        inputs = driver.find_elements_by_css_selector("input.sc-dEoRIm.drdMJh")
        time.sleep(random.random())
        send_keys(inputs[0], task.account.email)
        time.sleep(random.random())
        send_keys(inputs[1], task.account.password)
        time.sleep(random.random())
        driver.find_element_by_css_selector("button.sc-kGXeez.kgGtxX").click()

        structure = ujson.loads(task.info)

        category = structure["input_category"]

        final_category = driver.find_element_by_id(f"category_item-{category}")

        try:
            time.sleep(random.random())
            final_category.click()
        except ElementNotInteractableException:
            sub_final_category = final_category.find_element_by_xpath("../../../a")

            try:
                time.sleep(random.random())
                sub_final_category.click()
                time.sleep(random.random())
                final_category.click()
            except ElementNotInteractableException:
                time.sleep(random.random())
                sub_final_category.find_element_by_xpath("../../../a").click()
                time.sleep(random.random())
                sub_final_category.click()
                time.sleep(random.random())
                final_category.click()

        inputs = driver.find_elements_by_xpath("//form[@id='aiform']//input")
        textareas = driver.find_elements_by_xpath("//form[@id='aiform']//textarea")
        selects = driver.find_elements_by_xpath("//form[@id='aiform']//select")

        for input_ in inputs:
            input_type = input_.get_attribute("type")
            input_id = input_.get_attribute("id")

            if not input_id:
                continue

            input_response = structure[input_id]

            if input_type == "text":
                time.sleep(random.random())
                send_keys(input_, input_response)
            elif input_type == "checkbox" or input_type == "radio":
                if input_response and not input_.is_selected():
                    time.sleep(random.random())
                    input_.click()

        for textarea in textareas:
            time.sleep(random.random())
            send_keys(textarea, structure[textarea.get_attribute("id")])

        for select in selects:
            select_id = select.get_attribute("id")
            select = Select(select)
            time.sleep(random.random())
            select.select_by_visible_text(structure[select_id])

        time.sleep(random.random())
        driver.find_element_by_id("aiform").submit()

        time.sleep(random.random())
        driver.find_element_by_class_name("sc-jAaTju ithrdG").click()
        time.sleep(random.random())
        driver.find_elements_by_class_name("sc-kGXeez cVvyrS").click()

        time.sleep(random.random())
        driver.find_elements_by_class_name("sc-cmjSyW kMnmL").click()

    except Exception as exception:
        print(exception)


def run_mercado_livre_task(task):
    pass


def run_task(task):
    if task.site == database.SiteEnum("OLX"):
        run_olx_task(task)
    else:
        run_mercado_livre_task(task)
