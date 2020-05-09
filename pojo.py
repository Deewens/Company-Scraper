'''
-------------------------------------
|           POJO CLASS              |
|       Author : Adrien Dudon       |
-------------------------------------
'''

class Organization:
    def __init__(self, org_name, org_city, org_country, org_id=None):
        self.org_name = org_name
        self.org_city = org_city
        self.org_country = org_country
        self.org_id = org_id


class Person:
    def __init__(self, last_name, first_name, job_title, phone, address, mail, linkedin_url, id=None):
        self.last_name = last_name
        self.first_name = first_name
        self.job_title = job_title
        self.phone = phone
        self.address = address
        self.mail = mail
        self.linkedin_url = linkedin_url
        self.id = id
