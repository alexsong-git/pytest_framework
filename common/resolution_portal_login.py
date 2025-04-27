from selenium.webdriver.common.by import By



def resolution_portal_login(driver, email, order):

    ele_email = driver.find_element(By.ID, "email")
    ele_email.send_keys(email)
    ele_orderNumber = driver.find_element(By.ID, "orderNumber")
    ele_orderNumber.send_keys(order)
    ele_button = driver.find_element(By.XPATH, "//button/span[text()='Next']")
    ele_button.click()
    element = driver.find_element(By.XPATH, "//div[text()='Seel protection overview']").text

    return element