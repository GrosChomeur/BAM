import sqlite3
from random import randint

con = sqlite3.connect("BAM.db")
cur = con.cursor()

def creer_base(h_ouverture : int, min_ouverture : int, h_fermeture : int, min_fermeture : int, nb_1place : int, nb_2places : int) -> None:
    """
    Initialise la base de données avec les tables nécessaires pour la gestion des locations de kayaks.
    """
    #Active les clés étrangères
    cur.execute("PRAGMA foreign_keys = ON")
    
    #Empêche plusieurs enregistrements
    tables = ['location', 'kayak', 'client', 'boutique_location', 'calendrier'] #Nom de toutes les tables qui vont(ou qui sont déjà) présentent dans BAM.db
    for e in tables:
        cur.execute(f"DROP TABLE IF EXISTS {e}")
    

    # --- Création de la table boutique_location ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS boutique_location(
        h_ouverture INT,
        min_ouverture INT,
        h_fermeture INT,
        min_fermeture INT,
        stock_1place INT CHECK (stock_1place <= 50 AND stock_1place >= 0),
        stock_2place INT CHECK (stock_2place <= 50 AND stock_2place >= 0)
        )
    """)
    #On met dans la table boutique_location les infos passées en paramètre de la fonction
    cur.execute("INSERT INTO boutique_location VALUES (?, ?, ?, ?, ?, ?)", (h_ouverture, min_ouverture, h_fermeture, min_fermeture, nb_1place, nb_2places))

    # --- Création de la table calendrier ---
    #On initialise en 01/01/2026 arbitrairement
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS calendrier( 
        annee INT,
        mois INT,
        jour INT
        )
    """)
    cur.execute("INSERT INTO calendrier VALUES (2026, 1, 1)")

    # --- Création de la table client ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS client(
        email TEXT PRIMARY KEY,
        nom TEXT,
        prenom TEXT
        )
    """)

    # --- Création de la table location ---
    # Ajout du parcours pour les calculs de retour
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS location(
        id_location INTEGER PRIMARY KEY AUTOINCREMENT,
        email INT REFERENCES client(email),
        nb_1place INT CHECK (nb_1place >= 0),
        nb_2places INT CHECK (nb_2places >= 0),
        parcours INT CHECK (parcours IN (0, 1)),
        a_depart INT, 
        m_depart INT, 
        j_depart INT,
        h_depart INT CHECK (h_depart >= {h_ouverture} AND h_depart <= {h_fermeture}-3),
        min_depart INT CHECK (min_depart >= 0 AND min_depart < 60)
        )
    """)
    
    con.commit()
    print("Base de données initialisée")
    


def date(j: int, m: int, a: int) -> None:
    """
    Met à jour la date dans la table 'calendrier' de la base de données. 
    
    Paramètres: j (int): Jour de la date 
                m (int): Mois de la date 
                a (int): Année de la date 
    """
    cur.execute("""UPDATE calendrier SET jour = ?, mois = ?, annee = ?""", (j, m, a))
    print(f"Date mise à jour : {j}/{m}/{a}")
    con.commit()



def jour_suivant() -> tuple[int, int, int] :
    """
    Fait passer un jour dans la base de données
    """
    cur.execute("SELECT * FROM calendrier")
    a, m, j = cur.fetchone() # met les 3 valeurs du tuple retournées pas la méthode fetchone (de la forme (annee, mois, jour)) dans les variables a, m et j.

    # Année bissextile ou non
    if a % 4 == 0 :
        if m in [1,3,5,7,8,10,12] : # ------------erreurs dans le premier fichier python sur les mois à 31 #### les mois a 31 jours sont [1,3,5,7,8,10,12], dit moi si je me trompe
            max_j = 31
        elif m == 2 :
            max_j = 29
        else :
            max_j = 30
    else :
        if m in [1,3,5,7,8,10,12] :
            max_j = 31
        elif m == 2 :
            max_j = 28
        else :
            max_j = 30
            
    # Si on doit changer de mois sinon incrémentation du jour
    if max_j == j :
        if m == 12 :
            m = 1
            a +=1
        else :
            m += 1
        j = 1
    else :
        j += 1

    return (j, m, a)


def ajouter_client(email : str, nom: str, prenom: str) -> bool :
    """
    Renvoie True s'il existe déjà, sinon l'ajoute et Renvoie False.
    """
    # On cherche si client il y a
    cur.execute("SELECT email FROM client WHERE email = ? AND nom = ? AND prenom = ?", (email, nom, prenom))

# AJOUT(?) : adresse email pour prénoms pareils

    resultat = cur.fetchone()
    # Si le client existe deja (On considère que 2 personnes n'ont pas le même nom et prenom...)
    if resultat is not None:
        return True # On renvoie True car le client existe deja
    # Sinon on l'ajoute
    else:
        cur.execute("INSERT INTO client (email, nom, prenom) VALUES (?, ?, ?)", (email, nom, prenom)) # On ajoute le client
        con.commit()
        print("Client", prenom, nom, "ajouté")
        return False
    
        # cur.execute("SELECT id_client FROM client WHERE nom = ? AND prenom = ?", (nom, prenom))
        # au cas ou le max n'est pas le dernier ajouté en cas de suppression de client



def ajoute_resa(j_depart: int, m_depart: int, a_depart: int, h_depart: int, min_depart: int, nb_1place: int, nb_2places: int, parcours: int, email_client: str) -> None:
    """
    Ajoute la location dans la base de données si elle est valide
    """
    print(h_depart, "h", min_depart, ",", nb_1place, "une place,", nb_2places, "deux places,", f"parcours {parcours}")

    # Vérification du nombre de kayaks demandés
    if nb_1place < 0 or nb_2places < 0 or (nb_1place == 0 and nb_2places == 0):
        print("Réservation impossible, nombre de kayaks invalide")
        return

    # Verification de la validité de la date
    if m_depart < 1 or m_depart > 12 or j_depart < 1 or j_depart > 31 : # vérification par rapport aux mois ??
        print("Réservation impossible, date invalide")
        return

    # Vérification de la cohérence de la date : avant/après la date actuelle
    cur.execute("""SELECT annee, mois, jour FROM calendrier""")
    a_actu, m_actu, j_actu = cur.fetchone()
    if (a_depart, m_depart, j_depart) < (a_actu, m_actu, j_actu): # <= , si on veut accepter les réservations pour le jour même
        print("Réservation impossible")
        return

    # Vérification de l'heure de départ en fonction du parcours
    if parcours == 0 and h_depart > 14 :   # si on veut autoriser les réservations pour 15h00 :   ... and (h_depart > 15 or (h_depart == 15 and min_depart > 0))
        print("Parcours de 6km non autorisé après 15h")
        return
    elif parcours == 1 and h_depart > 13 :   # si on veut autoriser les réservations pour 14h00 :   ... and (h_depart > 14 or (h_depart == 14 and min_depart > 0))
        print("Parcours de 10km non autorisé après 14h")
        return

    # Vérification de l'email du client
    cur.execute("""SELECT email FROM client WHERE email = ?""", (email_client,))
    if cur.fetchone() is None:
        print(f"Le client avec l'email : {email_client} n'existe pas.")
        return



    # Vérification du stock de la JOURNEE (on peut prendre au max 100 kayaks réservés logiquement)
    cur.execute("""
        SELECT SUM(nb_1place), SUM(nb_2places) 
        FROM location 
        WHERE a_depart = ? AND m_depart = ? AND j_depart = ?""", 
        (a_depart, m_depart, j_depart))
    resultat = cur.fetchone()

    # Verification de valeurs None
    if resultat[0] is None:
        resultat = (0, resultat[1])
    if resultat[1] is None:
        resultat = (resultat[0], 0)
    
    # Comparaison avec le stock total
    """if (50 - resultat[0] < nb_1place) or (50 - resultat[1] < nb_2places):
        print("Réservation impossible, pas assez de kayaks disponibles")
        return"""

    # fin vérification stock pour une journée




    ######### En prenant en compte les retours de kayaks #########

    cur.execute("""
        SELECT SUM(nb_1place), SUM(nb_2places) 
        FROM location 
        WHERE a_depart = ? AND m_depart = ? AND j_depart = ? AND (h_depart < ? OR (h_depart = ? AND min_depart <= ?))""", 
        (a_depart, m_depart, j_depart, h_depart, h_depart, min_depart))
    resultat_retours = cur.fetchone()
    
    # Verification de valeurs None
    if resultat_retours[0] is None:
        resultat_retours = (0, resultat_retours[1])
    if resultat_retours[1] is None:
        resultat_retours = (resultat_retours[0], 0)

    # Liste de tuples (heure, minute, nb_kayaks à ramasser) : [(12,30,nb), (13,30,nb), ...]
    rk2p = retour_kayaks2places(j_depart, m_depart, a_depart)
    rk1p = retour_kayaks1place(j_depart, m_depart, a_depart)
    print(f"{rk1p=}")
    print(f"{rk2p=}")


    # Calcul du nombre de kayaks 1 places ramenés avant l'heure de départ
    S1=0
    i = 0
    # parcours 0
    while (h_depart, min_depart) > (rk1p[0][i][0], rk1p[0][i][1]) and i < len(rk1p[0]):
        S1 += rk1p[0][i][2]
        i += 1
    # parcours 1
    while (h_depart, min_depart) > (rk1p[1][i][0], rk1p[1][i][1]) and i < len(rk1p[1]):
        S1 += rk1p[1][i][2]
        i += 1

    # Calcul du nombre de kayaks 2 place ramenés avant l'heure de départ
    S2=0
    i = 0
    # parcours 0
    while (h_depart, min_depart) > (rk2p[0][i][0], rk2p[0][i][1]) and i < len(rk2p[0]):
        S2 += rk2p[0][i][2]
        i += 1
    # parcours 1
    while (h_depart, min_depart) > (rk2p[1][i][0], rk2p[1][i][1]) and i < len(rk2p[1]):
        S2 += rk2p[1][i][2]
        i += 1
    

    print((50 + S1 - resultat[0] < nb_1place), f"{S1=}, {nb_1place=}, {resultat[0]=}")
    print((50 + S2 - resultat[1] < nb_2places), f"{S2=}, {nb_2places=}, {resultat[1]=}")
    # On ajoute les kayaks ramenés avant l'heure de départ
    # Comparaison avec le stock total
    if (50 + S1 - resultat[0] < nb_1place) or (50 + S2 - resultat[1] < nb_2places):
        print("Réservation impossible, pas assez de kayaks disponibles\n")
        return


    


    # Insertion de la réservation
    cur.execute("""
        INSERT INTO location (email, nb_1place, nb_2places, parcours, a_depart, m_depart, j_depart, h_depart, min_depart) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (email_client, nb_1place, nb_2places, parcours, a_depart, m_depart, j_depart, h_depart, min_depart))
    con.commit()
    print("Réservation par", email_client, "prise en compte\n")
    




def supprime_resa(id_location : int, j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int):
    """
    Supprime une location si la date n'a pas été dépassée
    """

    # Si location est plus ancienne que la date -> On ne peut pas la supprimer
    cur.execute("""SELECT * FROM calendrier""")
    if cur.fetchone() < (a_depart, m_depart, j_depart) : #Verifie si la date est strictement plus petite que la date de la location
        cur.execute(f"""DELETE FROM location WHERE id_location = {id_location}""")
        con.commit()
        print("Réservation supprimée")
    else :
        print("Impossible de supprimer une réservation passée")

        
def retour_kayaks2places(j_depart: int, m_depart: int, a_depart: int):
    """
    Renvoie les horaires de ramassage des kayaks 2 places.
    """
    #On extrait les données chronologiquement pour que ce soit plus facile, donc pas besoin de tri ou de fonction la sorted()
    cur.execute("""
        SELECT nb_2places, parcours, h_depart, min_depart 
        FROM location 
        WHERE nb_2places > 0 
        AND a_depart = ? AND m_depart = ? AND j_depart = ?
        ORDER BY h_depart, min_depart """, 
        (a_depart, m_depart, j_depart))
    
    rows = cur.fetchall()
    #L'employé passe toutes les 30 min
    #Fin du parcours 0 : 12h30, 13h30..., 18h30
    ramassage0 = [(12 + i, 30) for i in range(7)]   # on rajoute un passage de l'employé à 18h30 et 19h pour ramasser les kayaks arrivant après 17h30 et 18h
    #Fin du parcours 1 : 13h00, 14h00..., 19h00
    ramassage1 = [(13 + i, 0) for i in range(7)]

    parcours0 = []
    parcours1 = []

    #Tableaux avec les horaires d'arrivée pour chaque parcours
    for i in range(len(rows)):
        row = list(rows[i])
        row[2] += 3 + row[1]
        if row[1] == 0 :
            parcours0.append(tuple(row))
        else :
            parcours1.append(tuple(row))


    # On calcule le nombre de kayaks à ramasser à chaque passage à chaque horaire pour le parcours 0 
    j = 0
    dict_parcours0 = {k:0 for k in range(len(ramassage0))}
    i = 0
    while i < len(parcours0) and j < len(ramassage0):
        if parcours0[i][2:4] <= ramassage0[j]:
            if (dict_parcours0[j] + parcours0[i][0]) > 12  :  # limite de 12 kayaks par passage:
                temp = 12 - dict_parcours0[j]
                nb_reste = parcours0[i][0] - temp

                if nb_reste > 0 :
                    dict_parcours0[j] = 12
                    j += 1
                    while nb_reste >= 12:
                        dict_parcours0[j] = 12
                        j += 1
                        nb_reste -= 12
                    dict_parcours0[j] = nb_reste
                else:
                    dict_parcours0[j+1] += nb_reste
                    dict_parcours0[j] = 12
                    j+=1
            else:
                dict_parcours0[j] += parcours0[i][0]
            i += 1
        else :
            j += 1

    resultat0 = [ramassage0[k] + (dict_parcours0[k],) for k in range(len(ramassage0))] 


    # On calcule le nombre de kayaks à ramasser à chaque passage à chaque horaire pour le parcours 1
    j = 0
    dict_parcours1 = {k:0 for k in range(len(ramassage1))}
    i = 0
    while i < len(parcours1) and j < len(ramassage1):
        if parcours1[i][2:4] <= ramassage1[j]:
            if (dict_parcours1[j] + parcours1[i][0]) > 12  :  # limite de 12 kayaks par passage:
                temp = 12 - dict_parcours1[j]
                nb_reste = parcours1[i][0] - temp

                if nb_reste > 0:
                    dict_parcours1[j] = 12
                    j += 1
                    while nb_reste >= 12:
                        dict_parcours1[j] = 12
                        j += 1
                        nb_reste -= 12
                    dict_parcours1[j] = nb_reste
                else:
                    dict_parcours1[j+1] += nb_reste
                    dict_parcours1[j] = 12
                    j+=1
            else:
                dict_parcours1[j] += parcours1[i][0]
            i += 1
        else :
            j += 1
            
    resultat1 = [ramassage1[k] + (dict_parcours1[k],) for k in range(len(ramassage1))]

    return (resultat0, resultat1)


def retour_kayaks1place(j_depart: int, m_depart: int, a_depart: int):
    """
    Renvoie les horaires de ramassage des kayaks 1 place.
    """
    # On extrait les données chronologiquement pour que ce soit plus facile, donc pas besoin de tri
    cur.execute("""
        SELECT nb_1place, parcours, h_depart, min_depart 
        FROM location 
        WHERE nb_1place > 0 
        AND a_depart = ? AND m_depart = ? AND j_depart = ?
        ORDER BY h_depart, min_depart """, 
        (a_depart, m_depart, j_depart))
    
    rows = cur.fetchall()
    #L'employé passe toutes les 30 min
    #Fin du parcours 0 : 12h30, 13h30...
    ramassage0 = [(12 + i, 30) for i in range(7)]     # on rajoute un passage de l'employé à 18h30 et 19h pour ramasser les kayaks arrivant après 17h30 et 18h
    #Fin du parcours 1 : 13h00, 14h00...
    ramassage1 = [(13 + i, 0) for i in range(7)]

    parcours0 = []
    parcours1 = []

    #Tableaux avec les horaires d'arrivée pour chaque parcours
    for i in range(len(rows)):
        row = list(rows[i])
        row[2] += 3 + row[1]
        if row[1] == 0 :
            parcours0.append(tuple(row))
        else :
            parcours1.append(tuple(row))

    # On calcule le nombre de kayaks à ramasser à chaque passage à chaque horaire pour le parcours 0
    j = 0
    dict_parcours0 = {k:0 for k in range(len(ramassage0))}
    i = 0
    while i < len(parcours0) and j < len(ramassage0):
        if parcours0[i][2:4] <= ramassage0[j]:
            if (dict_parcours0[j] + parcours0[i][0]) > 12  :  # limite de 12 kayaks par passage:
                temp = 12 - dict_parcours0[j]
                nb_reste = parcours0[i][0] - temp

                if nb_reste > 0:
                    dict_parcours0[j] = 12
                    j += 1
                    while nb_reste >= 12:
                        dict_parcours0[j] = 12
                        j += 1
                        nb_reste -= 12
                    dict_parcours0[j] = nb_reste
                else:
                    dict_parcours0[j+1] += nb_reste
                    dict_parcours0[j] = 12
                    j+=1
            else:
                dict_parcours0[j] += parcours0[i][0]
            i += 1
        else :
            j += 1

    resultat0 = [ramassage0[k] + (dict_parcours0[k],) for k in range(len(ramassage0))] 


    # On calcule le nombre de kayaks à ramasser à chaque passage à chaque horaire pour le parcours 1
    j = 0
    dict_parcours1 = {k:0 for k in range(len(ramassage1))}
    i = 0
    while i < len(parcours1) and j < len(ramassage1):
        if parcours1[i][2:4] <= ramassage1[j]:
            if (dict_parcours1[j] + parcours1[i][0]) > 12  :  # limite de 12 kayaks par passage:
                temp = 12 - dict_parcours1[j]
                nb_reste = parcours1[i][0] - temp

                if nb_reste > 0:
                    dict_parcours1[j] = 12
                    j += 1
                    while nb_reste >= 12:
                        dict_parcours1[j] = 12
                        j += 1
                        nb_reste -= 12
                    dict_parcours1[j] = nb_reste
                else:
                    dict_parcours1[j+1] += nb_reste
                    dict_parcours1[j] = 12
                    j+=1
            else:
                dict_parcours1[j] += parcours1[i][0]
            i += 1
        else :
            j += 1
            
    resultat1 = [ramassage1[k] + (dict_parcours1[k],) for k in range(len(ramassage1))]

    return (resultat0, resultat1)

    
def kayak_dispo(j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int, nb_2places : int, parcours : int) -> bool :
    cur.execute(f"""SELECT SUM(nb_1place) FROM location WHERE j_depart = {j_depart} AND m_depart = {m_depart} AND a_depart = {a_depart}""")
    # on selectionne toutes les resa kayak une place et les somme
    # Donc 50 - cette somme = nb de kayak dispo sans ceux qui vont etre ramenés
    # c'est là où il faut utiliser retour_kayaks1place pour savoir combien de kayak vont etre ramenés avant l'heure de la nouvelle resa
    used_1 = cur.fetchall()


    # rassemble tous les kayaks 1 place utilisés durant le moment donné en entrée.
    cur.execute(f"""SELECT SUM(nb_2place) FROM location WHERE j_depart = {j_depart} AND m_depart = {m_depart} AND a_depart = {a_depart}""")
    used_2 = cur.fetchall()

    # dessous, observe si on peut utiliser les kayaks demandés en +.
    if used_1[0] + nb_1place <= 50 and used_2[0] + nb_2places <= 50:
        return True
    else:
        return False
    


creer_base(9, 0, 18, 0, 50, 50) 
a,m,j = jour_suivant()
date(a,m,j)
ajouter_client("dtc@trouduc.com", "Dick", "John")

print("\n--- Tests ---\n")

#ajoute_resa(14, 1, 2026, 10, 0, 2, 1, 0, "dtc@trouduc.com")
#print(retour_kayaks1place(14, 1, 2026))
#print(retour_kayaks2places(14, 1, 2026))

"""for i in range(60):
    a,m,j = jour_suivant()
    date(a,m,j)""" # test jour_suivant et date

ajoute_resa(7, 2, 2026, 9, 0, 50, 50, 0, "dtc@trouduc.com")
ajoute_resa(7, 2, 2026, 9, 0, 50, 50, 1, "dtc@trouduc.com")
ajoute_resa(7, 2, 2026, 12, 45, 10, 10, 1, "dtc@trouduc.com")
"""for i in range(15):
    ajoute_resa(7, 2, 2026, randint(9,14), randint(0,59), randint(0,10), randint(0,10), randint(0,1), "dtc@trouduc.com")"""
#ajoute_resa(7, 2, 2026, 14, 0, 12, 12, 0, "dtc@trouduc.com")

if __name__ == "__main__":
    con.commit()
    con.close()
