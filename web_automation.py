import random
import time
from tkinter import messagebox

import ujson
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

import database


def send_keys(input_, keys):
    for key in keys:
        input_.send_keys(key)
        time.sleep(random.random())


def create_task():
    accounts = database.get_accounts()

    if not accounts:
        return

    for account in database.get_accounts():
        try:
            driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
            driver.implicitly_wait(30)

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

            messagebox.showinfo(
                "Antes de prosseguir...",
                "Foi aberto um navegador, que entrou automaticamente na pagina "
                "de publicar anuncio no OLX. Coloque todas as informações e depois "
                "aperte em \"Ok\""
            )

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

            return structure

        except Exception as exception:
            print(exception)


def run_task(task):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(2)

    try:
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

        images_input = driver.find_element_by_class_name("box__field")

        for image in structure["images"]:
            images_input.send_keys(image)

        time.sleep(random.random())
        driver.find_element_by_id("aiform").submit()

        time.sleep(random.random())
        driver.find_element_by_class_name("sc-jAaTju ithrdG").click()
        time.sleep(random.random())
        driver.find_elements_by_class_name("sc-kGXeez cVvyrS").click()

        time.sleep(random.random())
        driver.find_elements_by_class_name("sc-cmjSyW kMnmL").click()

        database.complete_task(task, True)

    except:
        database.complete_task(task, False)

    finally:
        driver.quit()
