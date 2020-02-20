from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import argparse

class ControlPOE:
    '''
    Turns POE ports on GS100TP on/off
    '''
    name = 'ControlPOE'
    def __init__(self, ip, password):
        '''
        ip - string like 'http://192.168.0.191'
        password - password for the Netgear switch firmware 5.4.2.33
        '''
        self.ip = ip
        self.password = password
        self._login()
        
    def _login(self):
        self.timeout = 10
        self.driver = webdriver.Firefox() # needs properly installed selenium
        self.driver.get(self.ip)
        ## login ##
        elem = self.driver.find_element_by_name('pwd')
        elem.clear()
        elem.send_keys(self.password)
        elem.send_keys(Keys.RETURN)
        
    def _get_poe_control_page(self):                   
        ## click on POE menu option ##
        poe_menu_option_xpath = '/html/body/div/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/div/table/tbody/tr[2]/td[4]/a/img'
        WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located((By.XPATH, poe_menu_option_xpath)))
        WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located((By.XPATH, poe_menu_option_xpath)))
        self.driver.find_element(By.XPATH, poe_menu_option_xpath).click()
        ## click on 'Advanced' ##
        WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located((By.NAME, 'lvl2')))
        self.driver.find_element(By.NAME, 'lvl2').click()
        ## click on 'PoE Port Configuration' ##
        WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located((By.LINK_TEXT, 'PoE Port Configuration')))
        self.driver.find_element(By.LINK_TEXT, 'PoE Port Configuration').click()
        ## switch to maincontent frame ##
        WebDriverWait(self.driver, self.timeout).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'maincontent'))) # also doing driver.switch_to.frame('maincontent')
        WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located((By.NAME, 'CBox_1')))
        self.elems = self.driver.find_elements(By.NAME, 'CBox_1')
        
    def _apply_changes(self):
        # Why 'driver.switch_to.default_content' does not work?
        self.driver.switch_to_default_content()
        WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/table/tbody/tr[4]/td/table/tbody/tr[2]/td/table/tbody/tr/td/a[3]')))
        # click on Apply
        self.driver.find_element(By.XPATH, '/html/body/div/table/tbody/tr[4]/td/table/tbody/tr[2]/td/table/tbody/tr/td/a[3]').click()
        
    def turn_off_POE(self, ports):
        '''
        Turns off ports = [p_0, ..., p_n] where p_i is in {1, ..., 8}
        '''
        self._get_poe_control_page()
        for port in ports:
            self.elems[port].click()
            self.driver.find_element(By.XPATH, "//select[@name='poeAdminMode']/option[text()='Disable']").click()
        self._apply_changes()    
    
    def turn_on_POE(self, ports):
        '''
        Turns on ports = [p_0, ..., p_n] where p_i is in {1, ..., 8}
        '''
        self._get_poe_control_page()
        for port in ports:
            self.elems[port].click()
            self.driver.find_element(By.XPATH, "//select[@name='poeAdminMode']/option[text()='Enable']").click()
        self._apply_changes()
    
    def close(self):
        self.driver.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Turns ON/OFF POE ports on Netgear GS110TP (only?) via web interface using selenium. RFC3632 MIB seems to be not implemented on this switch and thus turning ON/OFF is not possible via snmp.')
    parser.add_argument('-ip', '--ip_address', type = str, help = 'IP address of the switch', required = True)
    parser.add_argument('-p', '--password', help = 'password of the switch', required = True)
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-on', '--ports_on', nargs='+' ,help = 'ports to be turned on; p_0 p_1 ... p_n where p_i in {1, ..., 8}')
    group.add_argument('-off', '--ports_off', nargs='+', help = 'ports to be turned off; p_0 p_1 ... p_n where p_i in {1, ..., 8}')
    
    args = parser.parse_args()
    ip = args.ip_address
    password = args.password
    ports_on  = None
    ports_off = None
    if args.ports_on != None:
        ports_on = [ int(port) for port in args.ports_on]
    if args.ports_off != None:
        ports_off = [ int(port) for port in  args.ports_off]
    
    c = ControlPOE('http://{0}'.format(ip), password)
    if ports_on != None:
        c.turn_on_POE(ports_on)
    if ports_off != None:
        c.turn_off_POE(ports_off)
    c.close()    
