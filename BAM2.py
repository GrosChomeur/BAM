import sqlite3

con = sqlite3.connect("BAM.db")
cur = con.cursor()

def creer_base(h_ouverture : int, min_ouverture : int, h_fermeture : int, min_fermeture : int, nb_1place : int, nb_2places : int) -> None:
    """
    Initialise la base de données avec les tables nécessaires pour la gestion des locations de kayaks en fonction des paramètres fournis.
    
    Tables :    boutique_location : informations sur les horaires d'ouverture/fermeture et le stock de kayaks
                calendrier : date actuelle
                client : informations sur les clients
                location : informations sur les locations effectuées ou passées
    
    Paramètres: h_ouverture (int) : Heure d'ouverture
                min_ouverture (int) : Minute d'ouverture
                h_fermeture (int) : Heure de fermeture
                min_fermeture (int) : Minute d'ouverture
                nb_1place (int) : Nombre de kayaks 1 place que la boutique possède
                nb_2place (int) : Nombre de kayaks 2 places que la boutique possède
    """
    # Active les clés étrangères
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Empêche plusieurs enregistrements en faisant un reset des tables
    tables = ['location', 'kayak', 'client', 'boutique_location', 'calendrier'] # Nom de toutes les tables qui sont présentent dans BAM.db
    for e in tables:
        cur.execute(f"DROP TABLE IF EXISTS {e}")
    
    if nb_1place < 0 or nb_2places < 0:
        raise ValueError("Le nombre de kayaks ne peut pas être négatif")

    if (h_ouverture, min_ouverture) >= (h_fermeture, min_fermeture):
        raise ValueError("L'heure d'ouverture doit être avant l'heure de fermeture")
    
    
    # --- Création de la table boutique_location ---
    # On vérifie de manière minimale la validité des heures et des stocks, on considère que les paramètres passés à la fonction sont relativement valides.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS boutique_location(
        h_ouverture INT CHECK (h_ouverture >= 0 AND h_ouverture < 24),
        min_ouverture INT CHECK (min_ouverture >= 0 AND min_ouverture < 60),
        h_fermeture INT CHECK (h_fermeture >= 0 AND h_fermeture < 24),
        min_fermeture INT CHECK (min_fermeture >= 0 AND min_fermeture < 60),
        stock_1place INT CHECK (stock_1place <= 50 AND stock_1place >= 0),
        stock_2places INT CHECK (stock_2places <= 50 AND stock_2places >= 0)
        )
    """)
    # On met dans la table boutique_location les infos passées en paramètre de la fonction
    cur.execute("INSERT INTO boutique_location VALUES (?, ?, ?, ?, ?, ?)", (h_ouverture, min_ouverture, h_fermeture, min_fermeture, nb_1place, nb_2places))

    # --- Création de la table calendrier ---
    # On initialise en 01/01/2026 arbitrairement
    
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
    cur.execute("""
    CREATE TABLE IF NOT EXISTS location(
        id_location INTEGER PRIMARY KEY AUTOINCREMENT,
        email INT REFERENCES client(email),
        nb_1place INT,
        nb_2places INT,
        parcours INT,
        a_depart INT, 
        m_depart INT, 
        j_depart INT,
        h_depart INT,
        min_depart INT
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
        if m in [1,3,5,7,8,10,12] :
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
    Ajoute un client dans la table 'client' s'il n'existe pas déjà.
    Renvoie True si le client a été ajouté, False sinon.
    """
    # On select un client avec les informations données
    cur.execute("SELECT email FROM client WHERE email = ? AND nom = ? AND prenom = ?", (email, nom, prenom))
    resultat = cur.fetchone()

    # Si le client existe deja
    if resultat is not None:
        return False # On renvoie False car le client existe déjà
    
    # Sinon on l'ajoute à la table
    else:
        cur.execute("INSERT INTO client (email, nom, prenom) VALUES (?, ?, ?)", (email, nom, prenom))
        con.commit()
        print("Client", prenom, nom, "ajouté")
        return True
    



def ajoute_resa(j_depart: int, m_depart: int, a_depart: int, h_depart: int, min_depart: int, nb_1place: int, nb_2places: int, parcours: int, email_client: str) -> None:
    """
    Ajoute la location dans la table 'location' si elle est valide
    """

    cur.execute("""SELECT h_ouverture, min_ouverture, h_fermeture, min_fermeture FROM boutique_location""")
    h_ouv, min_ouv, h_fer, min_fer = cur.fetchone()

    # Vérification du nombre de kayaks demandés
    if nb_1place < 0 or nb_2places < 0 or (nb_1place == 0 and nb_2places == 0):
        print("Réservation impossible, nombre de kayaks invalide")
        return

    # Vérification du parcours
    if parcours not in [0, 1]:
        print("Réservation impossible, parcours invalide")
        return

    # Verification de la validité de la date et de l'horaire
    if m_depart < 1 or m_depart > 12 or j_depart < 1 or j_depart > 31 or h_depart < 0 or h_depart > 23 or min_depart < 0 or min_depart >= 60:
        print("Réservation impossible, date invalide")
        return

    # Vérification de la cohérence de la date : avant/après la date actuelle
    cur.execute("""SELECT annee, mois, jour FROM calendrier""")
    a_actu, m_actu, j_actu = cur.fetchone()
    if (a_depart, m_depart, j_depart) <= (a_actu, m_actu, j_actu): # On ne peut pas réserver pour une date passée ou le jour même
        print("Réservation impossible : date passée")
        return



    # Vérification de l'heure de départ en fonction du parcours (On exclut les résa pour 15h et 14h pour les parcours 0 et 1 respectivement)
    if parcours == 0 and h_depart > h_fer - 3 :
        print(f"Parcours de 6km non autorisé après {h_fer - 3}h00")
        return
    elif parcours == 1 and h_depart > h_fer - 4 :
        print(f"Parcours de 10km non autorisé après {h_fer - 4}h00")
        return

    # Vérification de l'email du client
    cur.execute("""SELECT email FROM client WHERE email = ?""", (email_client,))
    if cur.fetchone() is None:
        print(f"Le client avec l'email : {email_client} n'existe pas, un compte est nécessaire pour effectuer une réservation")
        return



    # 1ère méthode : Vérification du stock en excluant les kayaks retournés par l'employé (on peut prendre au max 100 kayaks réservés logiquement, avec 50 de chaque type)
    '''cur.execute("""
        SELECT SUM(nb_1place), SUM(nb_2places) 
        FROM location 
        WHERE a_depart = ? AND m_depart = ? AND j_depart = ?""", 
        (a_depart, m_depart, j_depart))
    resultat = cur.fetchone()

    # Verification de valeurs None et remplacement par des 0
    if resultat[0] is None:
        resultat = (0, resultat[1])
    if resultat[1] is None:
        resultat = (resultat[0], 0)
    
    # Comparaison avec le stock total
    """if (50 - resultat[0] < nb_1place) or (50 - resultat[1] < nb_2places):
        print("Réservation impossible, pas assez de kayaks disponibles")
        return"""'''
    # fin vérification 1ère méthode



    # 2ème méthode : Vérification du stock en incluant les kayaks retournés par l'employé
    cur.execute("""
        SELECT SUM(nb_1place), SUM(nb_2places) 
        FROM location 
        WHERE a_depart = ? AND m_depart = ? AND j_depart = ?""", 
        (a_depart, m_depart, j_depart))
    resultat_retours = cur.fetchone()
    
    # Verification de valeurs None et remplacement par des 0
    if resultat_retours[0] is None:
        resultat_retours = (0, resultat_retours[1])
    if resultat_retours[1] is None:
        resultat_retours = (resultat_retours[0], 0)

    # Liste de tuples (heure, minute, nb_kayaks à ramasser), exemple : ([(12,30,3), (13,30,8), ...], [(13,0,5), (14,0,12), ...])
    rk2p = retour_kayaks2places(j_depart, m_depart, a_depart)
    rk1p = retour_kayaks1place(j_depart, m_depart, a_depart)


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
    
    cur.execute("""SELECT stock_1place, stock_2places FROM boutique_location""")
    stock = cur.fetchone()

    # Comparaison avec le stock total + les retours
    if (stock[0] + S1 - resultat_retours[0] < nb_1place) or (stock[1] + S2 - resultat_retours[1] < nb_2places):
        print("Réservation impossible, pas assez de kayaks disponibles\n")
        return
    # fin vérification 2ème méthode

    


    # Insertion de la réservation
    cur.execute("""
        INSERT INTO location (email, nb_1place, nb_2places, parcours, a_depart, m_depart, j_depart, h_depart, min_depart) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (email_client, nb_1place, nb_2places, parcours, a_depart, m_depart, j_depart, h_depart, min_depart))
    con.commit()
    print("Réservation par", email_client, "prise en compte\n")
    


def supprime_resa(id_location : int, j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int) -> None:
    """
    Supprime une location existante si la date n'a pas été dépassée
    """

    # Si la réservation est plus ancienne que la date -> On ne plus pas la supprimer, on ne peut pas supprimer une réservation le jour même
    cur.execute("""SELECT * FROM calendrier""")
    if cur.fetchone() < (a_depart, m_depart, j_depart) : # Verifie si la date actuelle est strictement plus petite que la date de la location
        cur.execute(f"""DELETE FROM location WHERE id_location = {id_location}""")
        con.commit()
        print("Réservation supprimée")
    else :
        print("Impossible de supprimer une réservation passée")

        
def retour_kayaks2places(j_depart: int, m_depart: int, a_depart: int):
    """
    Renvoie les horaires de ramassage des kayaks 2 places pour une date donnée en paramètre
    """
    cur.execute("""SELECT h_ouverture, min_ouverture, h_fermeture, min_fermeture FROM boutique_location""")
    h_ouv, min_ouv, h_fer, min_fer = cur.fetchone()
    
    # On extrait les données chronologiquement avec ORDER BY pour que ce soit plus facile à traiter
    cur.execute("""
        SELECT nb_2places, parcours, h_depart, min_depart 
        FROM location 
        WHERE nb_2places > 0 
        AND a_depart = ? AND m_depart = ? AND j_depart = ?
        ORDER BY h_depart, min_depart """, 
        (a_depart, m_depart, j_depart))
    rows = cur.fetchall()

    #On considère que l'employé passe toutes les 30 min alternativement entre chaque parcours en commençant par le parcours 0 :

    # Pour le parcours 0 : 12h30, 13h30..., 18h30
    ramassage0 = [(h_ouv + 3 + i, 30) for i in range(7)]   # on rajoute un passage de l'employé à 18h30 et 19h pour potentiellement ramasser les kayaks retardataires arrivant après 17h30 et 18h
    # Pour le parcours 1 : 13h00, 14h00..., 19h00
    ramassage1 = [(h_ouv + 4 + i, 0) for i in range(7)]

    #Tableaux avec les horaires d'arrivée triés par parcours
    parcours0 = []
    parcours1 = []
    for i in range(len(rows)):
        row = list(rows[i])
        row[2] += 3 + row[1]
        if row[1] == 0 :
            parcours0.append(tuple(row))
        else :
            parcours1.append(tuple(row))


    # On calcule le nombre de kayaks à ramasser à chaque passage de l'employé à chaque horaire pour le parcours 0 
    j = 0
    dict_parcours0 = {k:0 for k in range(len(ramassage0))}
    i = 0
    while i < len(parcours0) and j < len(ramassage0):
        if parcours0[i][2:4] <= ramassage0[j]:
            if (dict_parcours0[j] + parcours0[i][0]) > 12  :  # limite de 12 kayaks par passage
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



    # On calcule le nombre de kayaks à ramasser à chaque passage de l'employé à chaque horaire pour le parcours 1
    j = 0
    dict_parcours1 = {k:0 for k in range(len(ramassage1))}
    i = 0
    while i < len(parcours1) and j < len(ramassage1):
        if parcours1[i][2:4] <= ramassage1[j]:
            if (dict_parcours1[j] + parcours1[i][0]) > 12  :  # limite de 12 kayaks par passage
                temp = 12 - dict_parcours1[j]
                nb_reste = parcours1[i][0] - temp

                if nb_reste > 0 :
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
    Renvoie les horaires de ramassage des kayaks 1 place pour une date donnée en paramètre
    """
    cur.execute("""SELECT h_ouverture, min_ouverture, h_fermeture, min_fermeture FROM boutique_location""")
    h_ouv, min_ouv, h_fer, min_fer = cur.fetchone()

    # On extrait les données chronologiquement pour que ce soit plus facile à traiter
    cur.execute("""
        SELECT nb_1place, parcours, h_depart, min_depart 
        FROM location 
        WHERE nb_1place > 0 
        AND a_depart = ? AND m_depart = ? AND j_depart = ?
        ORDER BY h_depart, min_depart """, 
        (a_depart, m_depart, j_depart))
    
    rows = cur.fetchall()
    #L'employé passe toutes les 30 min
    # Pour le parcours 0 : 12h30, 13h30... 18h30
    ramassage0 = [(h_ouv + 3 + i, 30) for i in range(7)]     # on rajoute un passage de l'employé à 18h30 et 19h pour potentiellement ramasser les kayaks retardataires arrivant après 17h30 et 18h 
    # Pour le parcours 1 : 13h00, 14h00... 19h00
    ramassage1 = [(h_ouv + 4 + i, 0) for i in range(7)]


    # Tableaux avec les horaires d'arrivée par parcours
    parcours0 = []
    parcours1 = []
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
            if (dict_parcours0[j] + parcours0[i][0]) > 12  :  # limite de 12 kayaks par passage
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
            if (dict_parcours1[j] + parcours1[i][0]) > 12  :  # limite de 12 kayaks par passage
                temp = 12 - dict_parcours1[j]
                nb_reste = parcours1[i][0] - temp

                if nb_reste > 0 :
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

    
    


if __name__ == "__main__":
    # Exemple d'initialisation de la base de données
    creer_base(9, 0, 18, 0, 50, 50) 
    a,m,j = jour_suivant()
    date(a,m,j)
    ajouter_client("test@loc-kayak.fr", "Freak", "John")
    ajoute_resa(2, 1, 2026, 9, 0, 5, 3, 1, "test@]loc-kayak.fr")
    print(retour_kayaks1place(2, 1, 2026))
    print(retour_kayaks2places(2, 1, 2026))

    con.commit()
    con.close()
