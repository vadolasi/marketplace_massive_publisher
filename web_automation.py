import ujson
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

import database
import tasks


def olx():
    driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
    driver.implicitly_wait(30)

    print(
        "Foi aberto um navegador, que ira entrar automaticamente na pagina "
        "de publicar anuncio no OLX. Coloque todas as informações e depois "
        "aperte enter"
    )

    driver.get("https://olx.com.br/")
    driver.find_element_by_css_selector("a.sc-jAaTju.gshyPU").click()

    inputs = driver.find_elements_by_css_selector("input.sc-dEoRIm.drdMJh")
    inputs[0].send_keys("vitor036daniel@protonmail.com")
    inputs[1].send_keys("03dejunho")
    driver.find_element_by_css_selector("button.sc-kGXeez.kgGtxX").click()

    input()

    structure = {}

    inputs = driver.find_elements_by_xpath("//form[@id='aiform']//input")
    selects = driver.find_elements_by_xpath("//form[@id='aiform']//select")

    for input_ in inputs:
        input_type = input_.get_attribute("type")
        input_id = input_.get_attribute("id")

        if input_type == "text" or input_type == "hidden":
            structure[input_id] = input_.get_attribute("value")
        elif input_type == "checkbox" or input_type == "radio":
            structure[input_id] = input_.is_selected()
    
    for select in selects:
        select_id = select.get_attribute("id")
        select = Select(select)
        structure[select_id] = select.first_selected_option.text

    driver.quit()

    for task in database.add_tasks("OLX", ujson.dumps(structure)):
        tasks.add_task(task)

    #! ===================

    driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver.implicitly_wait(2)

    driver.get("https://olx.com.br/")
    driver.find_element_by_css_selector("a.sc-jAaTju.gshyPU").click()

    inputs = driver.find_elements_by_css_selector("input.sc-dEoRIm.drdMJh")
    # inputs[0].send_keys(task.account.email)
    # inputs[1].send_keys(task.account.password)
    inputs[0].send_keys("vitor036daniel@protonmail.com")
    inputs[1].send_keys("03dejunho")
    driver.find_element_by_css_selector("button.sc-kGXeez.kgGtxX").click()

    # structure = ujson.loads(task.info)

    category = structure["input_category"]

    final_category = driver.find_element_by_id(f"category_item-{category}")

    try:
        final_category.click()
    except ElementNotInteractableException:
        sub_final_category = final_category.get_element.find_element_by_xpath(".//ancestor::ul/following-sibling::a")

        try:
            sub_final_category.click()
        except ElementNotInteractableException:
            sub_final_category.get_element.find_element_by_xpath(".//ancestor::ul/following-sibling::a").click()
            sub_final_category.click()
            final_category.click()

    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, f"category_item-{category}"))).click()

    inputs = driver.find_elements_by_xpath("//form[@id='aiform']//input")
    selects = driver.find_elements_by_xpath("//form[@id='aiform']//select")

    for input_ in inputs:
        input_type = input_.get_attribute("type")
        input_id = input_.get_attribute("id")
        input_response = structure[input_id]

        if input_type == "text":
            structure[input_id] = input_.get_attribute("value")
            input_.send_keys(input_response)
        elif input_type == "checkbox" or input_type == "radio":
            if input_response and not input_.is_selected():
                input_.click()

    for select in selects:
        select_id = select.get_attribute("id")
        select = Select(select)
        select.select_by_visible_text(structure[select_id])


def run_olx_task(task):
    driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver.implicitly_wait(30)

    driver.get("https://olx.com.br/")
    driver.find_element_by_css_selector("a.sc-jAaTju.gshyPU").click()

    inputs = driver.find_elements_by_css_selector("input.sc-dEoRIm.drdMJh")
    inputs[0].send_keys(task.account.email)
    inputs[1].send_keys(task.account.password)
    driver.find_element_by_css_selector("button.sc-kGXeez.kgGtxX").click()

    structure = ujson.loads(task.info)

    category = structure["category"]

    driver.find_element_by_xpath(f"//a[starts-with(@id, 'category_item-')][title='{category}']").click()

    subcategory = structure.get("subcategory", None)

    if subcategory:
        driver.find_elements_by_xpath(f"//a[starts-with(@id, 'category_item-')][title='{subcategory}']").click()

    grandsoncategory = structure.get("grandsoncategory", None)

    if grandsoncategory:
        driver.find_element_by_xpath(f"//ul[@class='category-container__grandsoncategory']//a[starts-with(@id, 'category_item-')][title='{grandsoncategory}']").click()

    inputs = driver.find_elements_by_xpath("//form[@id='aiform']//input")
    selects = driver.find_elements_by_xpath("//form[@id='aiform']//select")

    for input_ in inputs:
        input_type = input_.get_attribute("type")
        input_id = input_.get_attribute("id")
        input_response = structure[input_id]

        if input_type == "text":
            structure[input_id] = input_.get_attribute("value")
            input_.send_keys(input_response)
        elif input_type == "checkbox" or input_type == "radio":
            if input_response and not input_.is_selected():
                input_.click()

    for select in selects:
        select_id = select.get_attribute("id")
        select = Select(select)
        select.select_by_visible_text(structure[select_id])

    driver.find_element_by_id("aiform").submit()

    driver.find_element_by_class_name("sc-jAaTju ithrdG").click()
    driver.find_elements_by_class_name("sc-kGXeez cVvyrS").click()

    driver.find_elements_by_class_name("sc-cmjSyW kMnmL").click()


def run_mercado_livre_task(task):
    pass


def run_task(task):
    if task.site == database.SiteEnum("OLX"):
        run_olx_task(task)
    else:
        run_mercado_livre_task(task)
