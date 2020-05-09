'''
-----------------------------------------
|       Scraper Database Module         |
|       Author : Damian Lallement       |
|   Database Author : Damian Lallement |
----------------------------------------
'''

from abc import ABC, abstractmethod
import mysql.connector
from pojo import Organization
from pojo import Person

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="projet_tutore_s3"
)

cursor = db.cursor()


class DB(ABC):
    @abstractmethod
    def insert(self, obj):
        pass

    @abstractmethod
    def update(self, obj):
        pass

    @abstractmethod
    def delete(self, obj):
        pass

    @abstractmethod
    def get_all(self):
        pass


class DBCompany(DB):
    def insert(self, organization):
        sql = "INSERT INTO entreprise(nom_ent, pays, ville) VALUES(%s, %s, %s)"
        values = (organization.org_name, organization.org_country, organization.org_city)

        cursor.execute(sql, values)
        db.commit()

        organization.org_id = cursor.lastrowid

        return True

    def update(self, organization):
        sql = "UPDATE entreprise SET nom_ent = %s, pays = %s, ville = %s WHERE no_ent = %s"
        values = (organization.org_name, organization.org_country, organization.org_city, organization.org_id)

        try:
            cursor.execute(sql, values)
            db.commit()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

        return True

    def delete(self, organization):
        sql = "DELETE FROM entreprise WHERE no_ent = %s"
        values = (organization.org_id,)

        cursor.execute(sql, values)
        db.commit()

        return True

    def get_all(self):
        org_list = []

        sql = "SELECT * FROM entreprise"
        cursor.execute(sql)

        row = cursor.fetchone()

        while row is not None:
            org = Organization(row[1], row[3], row[2], row[0])
            org_list.append(org)
            row = cursor.fetchone()

        return org_list

    def get_by_name(self, org_name):
        org_list = []

        sql = "SELECT * FROM entreprise WHERE nom_ent = %s"
        values = (org_name,)
        cursor.execute(sql, values)

        row = cursor.fetchone()

        while row is not None:
            org = Organization(row[1], row[3], row[2], row[0])
            org_list.append(org)
            row = cursor.fetchone()

        return org_list


class DBPerson(ABC):
    def insert(self, person):
        sql = "INSERT INTO personne(nom, prenom, nom_poste, no_tel, addr, email, linkedin_url) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        values = (person.last_name, person.first_name, person.job_title, person.phone, person.address, person.mail, person.linkedin_url)
        cursor.execute(sql, values)
        db.commit()

        person.id = cursor.lastrowid

        return True

    def update(self, person):
        sql = "UPDATE personne SET nom = %s, prenom = %s, nom_poste = %s, no_tel = %s, addr = %s, email = %s, linkedin_url = %s WHERE id_pers = %s"
        values = (person.last_name, person.first_name, person.job_title, person.phone, person.address, person.mail, person.linkedin_url, person.id)
        cursor.execute(sql, values)
        db.commit()

        return True

    def delete(self, person):
        sql = "DELETE FROM personne WHERE id_pers = %s"
        values = (person.id,)
        cursor.execute(sql, values)
        db.commit()

        return True

    def get_all(self):
        person_list = []
        sql = "SELECT * FROM personne"
        cursor.execute(sql)

        row = cursor.fetchone()

        while row is not None:
            person = Person(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[0])
            person_list.append(person)
            row = cursor.fetchone()

        return person_list

    def get_by_name(self, first_name, last_name):
        person_list = []

        sql = "SELECT * FROM personne WHERE nom = %s AND prenom = %s"
        values = (last_name, first_name)
        cursor.execute(sql, values)

        row = cursor.fetchone()

        while row is not None:
            person = Person(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[0])
            person_list.append(person)
            row = cursor.fetchone()

        return person_list

class DBEmployment:
    def insert(self, person_id, org_id):
        sql = "INSERT INTO emploi(id_pers, no_ent) VALUES(%s, %s)"
        values = (person_id, org_id)
        cursor.execute(sql, values)
        db.commit()

        return True