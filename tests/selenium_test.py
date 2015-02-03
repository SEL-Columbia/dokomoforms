"""Front-end tests"""
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from db.auth_user import auth_user_table
from db.submission import submission_table

base = 'http://localhost:8888'


def go_to_new_window(driver: WebDriver):
    """
    I think this is how you switch windows...?

    :param driver: the Selenium WebDriver
    """
    for handle in driver.window_handles:
        driver.switch_to.window(handle)


class DriverTest(unittest.TestCase):
    def setUp(self):
        self.drv = webdriver.Firefox()

    def tearDown(self):
        submission_table.delete().execute()
        auth_user_table.delete().where(
            auth_user_table.c.email == 'test@mockmyid.com').execute()
        self.drv.quit()


class AuthTest(DriverTest):
    def testLoginAndLogout(self):
        self.drv.get(base + '/')

        self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)

        self.drv.find_element_by_xpath('//*[@id="login"]').click()
        go_to_new_window(self.drv)
        eml = self.drv.find_element_by_xpath('//*[@id="authentication_email"]')
        eml.send_keys('test@mockmyid.com', Keys.RETURN)
        self.drv.switch_to.window(self.drv.window_handles[0])
        load = EC.presence_of_element_located((By.ID, 'logout'))
        WebDriverWait(self.drv, 10).until(load)

        self.assertIn('Welcome: test@mockmyid.com', self.drv.page_source)

        self.drv.find_element_by_id('logout').click()
        load2 = EC.presence_of_element_located((By.ID, 'login'))
        WebDriverWait(self.drv, 2).until(load2)

        self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)


class SubmissionTest(DriverTest):
    def testSubmitSuccessfully(self):
        # Log in
        self.drv.get(base + '/debug/login/test_email')
        self.drv.get(base + '/')

        # Click on the survey
        self.drv.find_element_by_xpath(
            '/html/body/div/div[3]/div[2]/ul/li/a').click()

        # Click on the shareable link
        WebDriverWait(self.drv, 2).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div[3]/div[1]/a')))
        self.drv.find_element_by_xpath(
            '/html/body/div[1]/div[3]/div[1]/a').click()

        # Fill out the survey
        WebDriverWait(self.drv, 2).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div/div[3]/input')))
        next_button = self.drv.find_element_by_class_name('page_nav__next')
        in_xpath = '/html/body/div/div[3]/'

        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('1')
        next_button.click()
        self.drv.find_element_by_xpath(in_xpath + 'select/option[2]').click()
        next_button.click()
        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('3.3')
        next_button.click()
        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('4/4/44')
        next_button.click()
        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('5:55')
        next_button.click()
        # browser geolocation is complicated in selenium...
        self.drv.execute_script(
            '''
            window.navigator.geolocation.getCurrentPosition =
              function (success) {
                var position = {"coords": {"latitude":  "40",
                                           "longitude": "-70"}
                               };
                success(position);
              }
            '''
        )
        self.drv.find_element_by_xpath(in_xpath + 'div[3]').click()
        next_button.click()
        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('text 7')
        next_button.click()
        self.drv.find_element_by_id('with_other').click()
        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('other 8')
        next_button.click()
        next_button.click()
        # TODO: Not really sure how to test the facility question...
        WebDriverWait(self.drv, 3).until(EC.presence_of_element_located(
            (By.XPATH, in_xpath + 'div[2]/div[1]/div[2]/div[3]/img[1]')))
        self.drv.find_element_by_xpath(
            in_xpath + 'div[2]/div[1]/div[2]/div[3]/img[1]').click()
        next_button.click()
        self.drv.find_element_by_xpath(in_xpath + 'div[2]').click()

        WebDriverWait(self.drv, 3).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div/div[4]/input')))

        # Check the submissions
        self.drv.get(base + '/')
        WebDriverWait(self.drv, 3).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div[3]/div[1]/ul/li/a')))
        self.drv.find_element_by_xpath(
            '/html/body/div[1]/div[3]/div[1]/ul/li/a').click()
        self.drv.find_element_by_xpath(
            '/html/body/div/div[3]/div[1]/ul/li/a').click()

        # Check the submission
        WebDriverWait(self.drv, 3).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div[3]/ul/li')))
        self.assertIn('Answer: 1', self.drv.page_source)


if __name__ == '__main__':
    unittest.main()

