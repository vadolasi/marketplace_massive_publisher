import random
import time
from tkinter import messagebox

import ujson
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

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
            options = Options() 
            options.add_argument("--disable-blink-features=AutomationControlled")
            driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install(), options=options)

            driver.get("https://olx.com.br/")
            time.sleep(random.random())
            driver.find_element_by_xpath("//*[@id='gatsby-focus-wrapper']/div[1]/div[1]/header/div[3]/div/a").click()
            time.sleep(random.random())
            send_keys(driver.find_element_by_xpath("//*[@id='__next']/div/div[1]/div[1]/div[2]/form/div[1]/div[2]/input"), account.email)
            time.sleep(random.random())
            send_keys(driver.find_element_by_xpath("//*[@id='__next']/div/div[1]/div[1]/div[2]/form/div[2]/div[2]/div/div/input"), account.password)
            time.sleep(random.random())
            driver.find_element_by_xpath("//*[@id='__next']/div/div[1]/div[1]/div[2]/form/button").click()

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
    options = Options() 
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install(), options=options)

    try:
        driver.get("https://olx.com.br/")
        time.sleep(random.random())
        driver.find_element_by_xpath("//*[@id='gatsby-focus-wrapper']/div[1]/div[1]/header/div[3]/div/a").click()
        time.sleep(random.random())
        send_keys(driver.find_element_by_xpath("//*[@id='__next']/div/div[1]/div[1]/div[2]/form/div[1]/div[2]/input"), task.account.email)
        time.sleep(random.random())
        send_keys(driver.find_element_by_xpath("//*[@id='__next']/div/div[1]/div[1]/div[2]/form/div[2]/div[2]/div/div/input"), task.account.password)
        time.sleep(random.random())
        driver.find_element_by_xpath("//*[@id='__next']/div/div[1]/div[1]/div[2]/form/button").click()

        structure = ujson.loads(task.info)

        category = structure["input_category"]


        time.sleep(random.random())
        driver.find_element_by_xpath(f"//*[starts-with(@id, 'category_item-{category[:-2]}')]").click()
        time.sleep(random.random())
        driver.find_element_by_xpath(f"//*[@id='category_item-{category}']").click()

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
            time.sleep(random.random())
            images_input.send_keys(image)

        time.sleep(random.random())
        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "ad_insertion_submit_button"))))
        time.sleep(random.random())
        time.sleep(random.random())
        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "ad_insertion_submit_button"))))

        time.sleep(random.random())
        driver.find_element_by_class_name("sc-jAaTju ithrdG").click()
        time.sleep(random.random())
        driver.find_element_by_class_name("sc-kGXeez cVvyrS").click()

        time.sleep(random.random())
        driver.find_element_by_class_name("sc-cmjSyW kMnmL").click()

        database.complete_task(task, True)

    except Exception as exception:
        print(exception)
        database.complete_task(task, False)

    finally:
        # driver.quit()
        pass
