from selenium.webdriver.common.by import By



def resolution_login(driver, email, order):

    ele_email = driver.find_element(By.ID, "login-email-input")
    ele_email.send_keys(email)
    ele_orderNumber = driver.find_element(By.ID, "login-order-id-input")
    ele_orderNumber.send_keys(order)
    ele_button = driver.find_element(By.ID, "login_next")
    ele_button.click()
    element = driver.find_element(By.ID, "ready_to_submit").text

    return element