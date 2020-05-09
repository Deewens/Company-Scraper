'''
-----------------------------------------
|       Scraper Database Module         |
|       Author : Damian Lallement       |
|   Database Author : Damiant Lallement |
----------------------------------------
'''

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="projet_tutore_s3"
)

#Noms d'entreprise déjà présente dans la Bdd Utile pour les Tests
c0 = mydb.cursor()
nom_ent = """Select nom_ent from entreprise"""
c0.execute(nom_ent)
d0 = c0.fetchall()
for row in d0:
  print(row)

#Récupération du numéro d'entreprise correspondant au nom
entreprise = (str(input("Saisissez le nom d'une Entreprise: ")),)
print("\n")
c1 = mydb.cursor(prepared=True)
no_ent = """Select no_ent from entreprise where nom_ent = %s"""
c1.execute(no_ent, entreprise)
d1 = c1.fetchone()

#Récupération du numéro d'identification des employés de l'entreprise
c2 = mydb.cursor(prepared=True)
id_pers = """Select id_pers from emploi where no_ent = %s"""
c2.execute(id_pers, d1)
d2 = c2.fetchall()



#Affichage des informations des employés
for row in d2:
    cursor = mydb.cursor(prepared=True)
    requete = """SELECT * FROM personne where id_pers =%s"""
    parametres = (row[0],)
    cursor.execute(requete, parametres)
    data = cursor.fetchall()

    for row in data:
     #Récupération du nom de poste des employés
     c3 = mydb.cursor(prepared=True)
     nom_poste = """SELECT nom_poste FROM personne where id_pers =%s"""
     p2 = (row[0],)
     c3.execute(nom_poste, p2)
     d3 = c3.fetchone()
    # Récupération de l'odre hierarchique des employés
    c6 = mydb.cursor(prepared=True)
    ordre_hier = """SELECT ordre_hierarchique FROM type_poste where nom_type_poste =%s """
    p4 = (d3[0].decode("utf-8"),)
    c6.execute(ordre_hier, p4)
    d6 = c6.fetchone()




