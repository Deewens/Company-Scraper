'''
-------------------------------------
|       Linkedin Scraper Module     |
|       Author : Adrien Dudon       |
-------------------------------------
'''


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import json
from database import DBCompany, DBPerson, DBEmployment
from pojo import Organization, Person

options = webdriver.ChromeOptions()
# options.add_argument('headless')  # Comment this line to open Chrome Browser and see the scrapping.
# options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument('disable-extensions')
# options.add_argument('no-sandbox')
# options.add_argument('disable-dev-shm-usage')

driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)


def get_data(org_name):
    # Connection to an account
    if not linkedin_account_connection('your_email', 'your_pwd'):
        print("Erreur durant l'authentification")
        return False
    else:
        print("Authentification a LinkedIn réussi.")

    url = get_linkedin_url(org_name)
    if not url:
        print("Impossible dé récuperer l'URL du profil LinkedIn de l'entreprise.")
        return False

    print("URL LinkedIn de l'entreprise récupéré, redirection...")
    driver.get(url)

    org_city = "/"
    org_country = "/"

    data = get_organization_data(org_name)
    if data:
        org_city = data["city_name"]
        org_country = data["country_code"]

    company_name = get_organization_name()
    employees_nb = get_employees_nb()
    employees_list = scrape_linkedin_employees_list()

    print("Sauvegarde des données récupéré en cours...")

    org_db = DBCompany()
    person_db = DBPerson()
    employment_db = DBEmployment()

    org = Organization(company_name, org_country, org_city)
    result = org_db.get_by_name(company_name)
    if not result:
        if not org_db.insert(org):
            print("Erreur lors de l'insertion de l'organisation dans la base de données.")
            return False
    else:
        org.org_id = result[0].org_id
        if not org_db.update(org):
            print("Erreur lors de la mise à jour des données de l'organisation dans la base de données.")
            return False

    for i in employees_list:
        # employees_linkedin = self.scrape_employees_linkedin_url(i)

        data = get_people_data(i)
        job_title = ""
        if data:
            if data["title"] is not None:
                job_title = data["title"]
                print(job_title)
        else:
            job_title = scrape_linkedin_job_title(employees_list[i])
            if not job_title:
                job_title = "Inconnu"

        names = i.split()
        first_name = names[0]
        last_name = names[1]

        person = Person(last_name, first_name, job_title, "/", "/", "/", employees_list[i])

        result = person_db.get_by_name(first_name, last_name)
        if not result:
            if not person_db.insert(person):
                print("Erreur lors de l'insertion de " + person.first_name + " " + person.last_name + "dans la "
                                                                                                      "base de "
                                                                                                      "données.")
            else:
                if not employment_db.insert(person.id, org.org_id):
                    print("Erreur lors de l'insertion dans la table 'emploi'.")
        else:
            person.id = result[0].id
            if not person_db.update(person):
                print(
                    "Erreur lors de la mise à jour de " + person.first_name + " " + person.last_name + "dans la base de données.")

    print("Sauvegarde terminé !")
    return True



def linkedin_account_connection(username, pwd):
    driver.get('https://www.linkedin.com/login')
    url = driver.current_url
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    print("Authentication to linkedin. Please wait...")
    time.sleep(0.5)
    try:
        username_input = driver.find_element_by_name('session_key')
        # username_input.send_keys(username)
        slow_typing(username_input, username)
    except NoSuchElementException:
        print("-- LINKEDIN AUTHENTICATION ERROR --\n"
              "Exception caught: unable to locate username input element.")
        return False

    time.sleep(0.5)
    try:
        pwd_input = driver.find_element_by_name('session_password')
        # pwd_input.send_keys(pwd)
        slow_typing(pwd_input, pwd)
    except NoSuchElementException:
        print("-- LINKEDIN AUTHENTICATION ERROR --\n"
              "Exception caught: unable to locate password input element.")
        return False
    time.sleep(0.5)

    log_in_button = driver.find_element_by_tag_name('button')
    log_in_button.click()

    time.sleep(0.5)

    try:
        username_error = driver.find_element_by_id('error-for-username')
        pwd_error = driver.find_element_by_id('error-for-password')
        if username_error.text:
            print("[LinkedIn] Username error:", username_error.text)
            return False

        if pwd_error.text:
            print("[LinkedIn] Password error:", pwd_error.text)
            return False
    except NoSuchElementException:
        pass

    # WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.ID, 'voyager-fed')))
    # print("[LinkedIn] Il semble y avoir une erreur (captcha), merci de la corriger.")

    return True


def get_linkedin_url(org_name):
    data = get_organization_data(org_name)
    if data:
        return data["linkedin_url"]
    else:
        """
        -----------------------
        | Google Query Search |
        ---------------------
        """
        driver.get('https://www.google.fr/')
        time.sleep(0.5)
        # Find the Google Search Bar
        search_query = driver.find_element_by_name('q')
        # Send a Google Query
        search_query.send_keys('site:linkedin.com/company/ AND "' + org_name + '"')
        search_query.send_keys(Keys.RETURN)
        search_result = driver.find_elements_by_class_name('r')
        if search_result:
            url_t = search_result[0].find_element_by_tag_name('a')
            url = url_t.get_attribute("href")
            print(url)
            return url

    return False


def scrape_employees_linkedin_url(name):
    data = get_people_data(name)
    if data:
        return data["linkedin_url"]
    else:
        """
        -----------------------
        | Google Query Search |
        ---------------------
        """
        driver.get('https://www.bing.com/')
        time.sleep(0.5)
        # Find the Google Search Bar
        search_query = driver.find_element_by_name('q')
        # Send a Google Query
        search_query.send_keys('site:linkedin.com/in/ AND "' + name + '"')
        search_query.send_keys(Keys.RETURN)
        url_t = ""
        url = ""
        search_result = driver.find_elements_by_class_name('b_attribution')
        if search_result:
            url_t = search_result[0].find_element_by_tag_name('cite')
            print(url_t.text)
            return url

    return False


def scrape_linkedin_employees_list():
    """
    ---------------------
    | Scrapping Linkedin |
    ---------------------
    """
    employees = driver.find_element_by_css_selector('a[data-control-name=topcard_see_all_employees]')
    employees_url = employees.get_attribute("href")
    driver.current_url

    driver.get(employees_url)
    time.sleep(0.5)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)
    indicator_number = driver.find_elements_by_class_name('artdeco-pagination__indicator--number')
    btn = indicator_number[len(indicator_number) - 1].find_element_by_tag_name('button')
    nb_page = btn.find_element_by_tag_name('span').text
    nb_page = int(nb_page)
    time.sleep(0.5)
    employees_name_list = []
    profile_url = []
    # Scrolling on the Web Page step by step to get all employees

    for page in range(1, nb_page + 1):
        time.sleep(1)
        if page > 1:
            driver.get(employees_url + "&page=" + str(page))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        list_emp = driver.find_elements_by_class_name('actor-name')

        link_url = driver.find_elements_by_xpath('//a[@data-control-name="search_srp_result"]')

        for url in link_url:
            if url.get_attribute('href') not in profile_url:
                if url.get_attribute('href').startswith('https://www.linkedin.com/in'):
                    profile_url.append(url.get_attribute('href'))

        for emp in list_emp:
            if emp.text != "Utilisateur LinkedIn":
                employees_name_list.append(emp.text)

    employees_dict = dict(zip(employees_name_list, profile_url))
    print(employees_dict)
    # site:linkedin.com/company/ AND "General Motors"
    return employees_dict


def scrape_linkedin_job_title(linkedin_url):
    driver.get(linkedin_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    section = driver.find_element_by_id('experience-section')
    company_background = section.find_elements_by_xpath('//a[@data-control-name="background_details_company"]')

    job_title = ""

    time.sleep(1)

    try:
        info = company_background[0].find_element_by_class_name(
            'pv-entity__summary-info--background-section')  # une seule
        print('Une expèrience')
        job_title = info.find_element_by_tag_name('h3').text
    except NoSuchElementException:
        pass

    try:
        info = company_background[0].find_element_by_class_name(
            'pv-entity__company-summary-info')  # plusieurs expèrience
        print('Plusieurs expèrience')
        company = info.find_element_by_tag_name('h3')
        h3 = company.find_elements_by_tag_name('span')
        company_name = h3[1]


        positions = section.find_elements_by_class_name('pv-entity__position-group')



        items = positions[0].find_elements_by_tag_name('li')


        job_title_h3 = items[0].find_element_by_tag_name('h3')

        job_title_span = job_title_h3.find_elements_by_tag_name('span')

        job_title = job_title_span[1].text
    except NoSuchElementException:
        pass

    return job_title


def get_employees_nb():
    employees = driver.find_element_by_css_selector('a[data-control-name=topcard_see_all_employees]')
    nb2 = employees.text
    nb = nb2.split()

    return nb[2]


def get_organization_name():
    title = driver.find_element_by_class_name('org-top-card-summary__title')

    return title.text


def slow_typing(element, text):
    for character in text:
        element.send_keys(character)
        # time.sleep(0.1)


'''
CRUNCHBASE
'''


def get_organization_data(org_name):
    url = "https://api.crunchbase.com/v3.1/odm-organizations?user_key=b354622a7d56ae0d7677e81940cb1019"
    querystring = {"query": org_name}

    response = requests.request("GET", url, params=querystring)

    x = response.text
    y = json.loads(x)

    if y["data"]["paging"]["total_items"] == 0:
        return False
    else:
        return y["data"]["items"][0]["properties"]


def get_people_data(name):
    url = "https://api.crunchbase.com/v3.1/odm-people?user_key=b354622a7d56ae0d7677e81940cb1019"

    querystring = {"query": name}

    response = requests.request("GET", url, params=querystring)

    x = response.text
    y = json.loads(x)
    if y["data"]["paging"]["total_items"] == 0:
        return False
    else:
        return y["data"]["items"][0]["properties"]
