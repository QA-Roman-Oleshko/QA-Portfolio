import time
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from faker import Faker

fake = Faker()

def setup_browser():
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver

@allure.feature("Процесс покупки на сайте")
@allure.story("Покупка товара и оформление заказа")
def test_purchase_and_checkout():
    browser = setup_browser()
    wait = WebDriverWait(browser, 30)

    try:
        with allure.step("Открытие сайта"):
            browser.get("https://magento-demo.mageplaza.com/")

        with allure.step("Поиск и выбор товара"):
            search_box = wait.until(EC.element_to_be_clickable((By.ID, "search")))
            search_box.send_keys("Strive Shoulder Pack")
            browser.find_element(By.CSS_SELECTOR, "button.action.search").click()

            product = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), 'Strive Shoulder Pack')]")))
            product.click()

        with allure.step("Добавление товара в корзину"):
            add_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.tocart")))
            add_btn.click()

        with allure.step("Ожидание и переход к корзине"):
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".message-success")))
            time.sleep(2)

            cart_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.action.showcart")))
            browser.execute_script("arguments[0].click();", cart_btn)

            checkout_btn = wait.until(EC.element_to_be_clickable((By.ID, "top-cart-btn-checkout")))
            checkout_btn.click()

        with allure.step("Заполнение формы доставки"):
            wait.until(EC.presence_of_element_located((By.ID, "customer-email")))
            time.sleep(2)  # Дать форме полностью прогрузиться

            email = fake.email()
            name = fake.first_name()
            lastname = fake.last_name()
            address = fake.street_address()
            city = fake.city()
            postcode = "10001"
            phone = fake.phone_number()

            browser.find_element(By.ID, "customer-email").send_keys(email)
            browser.find_element(By.NAME, "firstname").send_keys(name)
            browser.find_element(By.NAME, "lastname").send_keys(lastname)
            browser.find_element(By.NAME, "street[0]").send_keys(address)
            browser.find_element(By.NAME, "city").send_keys(city)

            Select(browser.find_element(By.NAME, "region_id")).select_by_index(1)
            browser.find_element(By.NAME, "postcode").send_keys(postcode)
            browser.find_element(By.NAME, "telephone").send_keys(phone)

            time.sleep(1)  # Подождать перед выбором метода доставки
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='flatrate_flatrate']"))).click()

        with allure.step("Переход к оплате"):
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-role='opc-continue']"))).click()

        with allure.step("Завершение заказа"):
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-mask[data-role='loader']")))
            place_order_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".action.primary.checkout")))
            place_order_btn.click()

        print("✅ Заказ успешно оформлен!")

    except (TimeoutException, ElementClickInterceptedException) as e:
        print(f"❌ Ошибка: {e}")
        raise
    finally:
        time.sleep(5)
        browser.quit()
