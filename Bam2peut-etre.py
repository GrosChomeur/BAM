import sqlite3

con = sqlite3.connect("BAM.db")
cur = con.cursor()

def creer_base(h_ouverture : int, min_ouverture : int, h_fermeture : int, min_fermeture : int, nb_1place : int, nb_2places : int) -> None:
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
        stock_1place INT CHECK (stock_1place <= 50), -----Max 50 kayaks de chaque type-----
        stock_2place INT CHECK (stock_2place <= 50)
        )
    """)
    #On met dans la table boutique_location les infos passées en paramètre de la fonction
    cur.execute("INSERT INTO boutique_location VALUES (?, ?, ?, ?, ?, ?)", (h_ouverture, min_ouverture, h_fermeture, min_fermeture, nb_1place, nb_2places))

    # --- Création de la table calendrier ---
    #On initialise en 01/01/2026 ?
    # g fait ca au pif 
    # C'est dangereux d'appeler une table 'date' sachant que date est un type en SQLite. ------------- Vrai j'y avait pas réflechi
    cur.execute("""
    CREATE TABLE IF NOT EXISTS calendrier( 
        annee INT,
        mois INT,
        jour INT
        )
    """)
    cur.execute("INSERT INTO calendrier VALUES (2026, 1, 1)")

    # --- Création de la table client --- ------------------ je ne sais pas si on doit s'occuper de la partie gestion des clients mais je suis d'accord que c'est important
    cur.execute("""
    CREATE TABLE IF NOT EXISTS client(
        id_client INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        prenom TEXT
        )
    """)

    # --- Création de la table kayak ---
    #On identifie chaque kayak pour mieux les gérer 

    ######################## On a pas du tout besoin de les gérer individuellement, donc je sais pas si c utile ##########################

    cur.execute("""
    CREATE TABLE IF NOT EXISTS kayak(
        id_kayak INTEGER PRIMARY KEY AUTOINCREMENT,
        type INT,
        etat TEXT DEFAULT 'disponible' ------------------- on fait pas de la gestion en live des nombres de kayaks dispo
        )
    """)
    
    #On remplie la table kayak avec les infos passées en paramètre de la fonction
    for _ in range(nb_1place):
        cur.execute("INSERT INTO kayak(type) VALUES (1)")
    for _ in range(nb_2places):
        cur.execute("INSERT INTO kayak(type) VALUES (2)")



    # --- Création de la table location ---
    # Ajout du parcours pour les calculs de retour
    cur.execute("""
    CREATE TABLE IF NOT EXISTS location(
        id_location INTEGER PRIMARY KEY AUTOINCREMENT,
        id_client INT REFERENCES client(id_client),
        nb_1place INT CHECK (nb_1place >= 0),
        nb_2places INT CHECK (nb_2places >= 0),
        parcours INT CHECK (parcours IN (0, 1)), -----0 pour débutant et 1 pour avancé
        a_depart INT, 
        m_depart INT, 
        j_depart INT,
        h_depart INT CHECK (h_depart >= 9 AND h_depart <= 15),
        min_depart INT CHECK (min_depart >= 0 AND min_depart < 60)
        )
    """)
    
    con.commit()
    print("Base de données initialisée")
    
#creer_base(9,00,18,00,50,50)

def date(j: int, m: int, a: int) -> None:
    """
    Met à jour la date dans la table 'calendrier' de la base de données. 
    
    Paramètres: j (int): Jour de la date 
                m (int): Mois de la date 
                a (int): Année de la date 
    """
    cur.execute("""UPDATE calendrier SET jour = ?, mois = ?, annee = ?""", (j, m, a))
    con.commit()

#date(14, 1, 2026)

def jour_suivant() -> tuple[int, int, int] :
    """
    Fait passer un jour dans la base de données
    """
    cur.execute("SELECT * FROM calendrier")
    a, m, j = cur.fetchone() # met les 3 valeurs du tuple retournées pas la méthode fetchone (de la forme (annee, mois, jour)) dans les variables a, m et j.

    #Année bissextile ou non
    if a % 4 == 0 :
        if m in [1,3,5,7,8,10,12] : #erreurs dans le premier fichier python sur les mois à 31 #### les mois a 31 jours sont [1,3,5,7,8,10,12], dit moi si je me trompe
            max_j = 31
        if m == 2 :
            max_j = 29
        else :
            max_j = 30
    else :
        if m in [1,3,5,7,8,10,12] :
            max_j = 31
        if m == 2 :
            max_j = 28
        else :
            max_j = 30
            
    #Si on doit changer de mois sinon incrémentation du jour
    if max_j == j :
        if m == 12 :
            m = 1
            a +=1
        else :
            m += 1
        j = 1
    else :
        j += 1
        
    cur.execute("""UPDATE calendrier SET jour = ?, mois = ?, annee = ?""", (j, m, a))
    con.commit()
    
jour_suivant()

def ajouter_client(nom: str, prenom: str) -> int:
    """
    Renvoie l'ID du client s'il existe déjà, sinon l'ajoute et Renvoie le nouvel ID.
    """
    # On cherche si client il y a
    cur.execute("SELECT id_client FROM client WHERE nom = ? AND prenom = ?", (nom, prenom))
    resultat = cur.fetchone()
    # Si le client existe deja (On considère que 2 personnes n'ont pas le même nom et prenom...)
    if resultat is not None:
        return resultat[0] # On renvoie l'id deja présent
    # Sinon on l'ajoute
    else:
        cur.execute("INSERT INTO client (nom, prenom) VALUES (?, ?)", (nom, prenom))
        cur.execute("SELECT MAX(id_client) FROM client") 

        # cur.execute("SELECT id_client FROM client WHERE nom = ? AND prenom = ?", (nom, prenom))
        # au cas ou le max n'est pas le dernier ajouté en cas de suppression de client

        id_cree = cur.fetchone()[0]
        con.commit()
        return id_cree # On renvoie le nouvel id
        
def ajoute_resa(j_depart: int, m_depart: int, a_depart: int, h_depart: int, min_depart: int, nb_1place: int, nb_2places: int, parcours: int, id_client: int) -> None:
    """
    Ajoute la location dans la base de données si elle est correcte.
    """
    #Vérification de la cohérence de la date
    cur.execute("""SELECT annee, mois, jour FROM calendrier""")
    a_actu, m_actu, j_actu = cur.fetchone()
    if (a_depart, m_depart, j_depart) < (a_actu, m_actu, j_actu): # <= ? on veut accepter les réservations pour le jour même ?
        print("Réservation impossible")
        return

    #Vérification de l'heure de départ en fonction du parcours
    if parcours == 0 and h_depart > 15 : # si 15h00 ?          ... and (h_depart > 15 or (h_depart == 15 and min_depart > 0))
        print("Parcours de 6km non autorisé après 15h")
        return
    elif parcours == 1 and h_depart > 14: # si 14h00 ?          ... and (h_depart > 14 or (h_depart == 14 and min_depart > 0))
        print("Parcours de 10km non autorisé après 14h")
        return

    #Vérification de l'id du client
    cur.execute("""SELECT id_client FROM client WHERE id_client = ?""", (id_client,))
    if cur.fetchone() is None:
        print(f"Le client numéro : {id_client} n'existe pas.")
        return

    #Vérification du stock de la JOURNEE (on peut prendre au max 100 réservé logiquement)
    cur.execute("""
        SELECT SUM(nb_1place), SUM(nb_2places) 
        FROM location 
        WHERE a_depart = ? AND m_depart = ? AND j_depart = ?""", 
        (a_depart, m_depart, j_depart))
    resultat = cur.fetchone()
    # Verification de valeurs None
    if resultat[0] is None:
        resultat[0] = 0
    if resultat[1] is None:
        resultat[1] = 0
    # Comparaison avec le stock total
    if resultat[0] < nb_1place or resultat[1] < nb_2places:
        print("Réservation impossible, pas assez de kayaks disponibles")
        return

    # Insertion de la réservation
    cur.execute("""
        INSERT INTO location (id_client, nb_1place, nb_2places, parcours, a_depart, m_depart, j_depart, h_depart, min_depart) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (id_client, nb_1place, nb_2places, parcours, a_depart, m_depart, j_depart, h_depart, min_depart))
    con.commit()
    print("Réservation prise en compte")
    
def supprime_resa(id_location : int, j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int):
    """
    Supprime une location si la date n'a pas été dépassée
    """

    # est-ce que la réservation existe
    cur.execute(f"""SELECT * FROM location WHERE id_location = {id_location}""")
    if cur.fetchone() is None :
        print("Cette réservation n'existe pas")
        return

    # est-ce que on considère que l'on peut supprimer une réservation le jour même ?

    # Si location est plus ancienne que la date -> On ne peut pas la supprimer
    cur.execute("""SELECT * FROM calendrier""")
    if cur.fetchone() <= (a_depart, m_depart, j_depart) : #Verifie si la date est plus petite qua la date de la location
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
    #Fin du parcours 0 : 12h30, 13h30...
    ramassage0 = [(12 + i, 30) for i in range(7)]
    #Fin du parcours 1 : 13h00, 14h00...
    ramassage1 = [(13 + i, 0) for i in range(6)]

    parcours0 = []
    parcours1 = []

    #Tableaux avec les horaires d'arrivée pour chaque parcours
    for i in range(len(rows)):
        row = list(rows[i])
        row[2] += 3 + row[1]
        if row[1] == 0 :
            parcours0.append(rows[i])
        else :
            parcours1.append(rows[i])
        
    j = 0
    dict_parcours0 = {k:0 for k in range(len(ramassage1))} #On met ramassage1 au lieu de ramassage0 plutôt
    i = 0
    #Ok mais si un kayak arrive après 17h30 a l'arrivée du parcours 0 ou après 18h a l'arrivée du parcours 1 on risque d'vaoir une erreur d'index il me semble (je suis pas sur mais a verifier)
    # j'ai ajouté une condition pour eviter l'erreur d'index
    # on peut rajouter un passage de l'employé à 18h30 pour ramasser les kayaks du parcours 0 arrivant après 17h30
    while i < len(parcours0) and j < len(ramassage0):
        if parcours0[i][2:4] <= ramassage0[j]:
            dict_parcours0[j] += parcours0[i][0]
            i += 1
        else :
            j += 1

    resultat0 = [ramassage0[k] + (dict_parcours0[k],) for k in range(len(ramassage0))] 

    j = 0
    dict_parcours1 = {k:0 for k in range(len(ramassage0))}
    i = 0
    while i < len(parcours1) and j < len(ramassage0):
        if parcours1[i][2:4] <= ramassage1[j]:
            dict_parcours1[j] += parcours1[i][0]
            i += 1
        else :
            j += 1
            
    resultat1 = [ramassage1[k] + (dict_parcours1[k],) for k in range(len(ramassage1))]

    return (resultat0, resultat1)


# --- A arranger ---       
def retour_kayaks2places(j_depart : int, m_depart : int, a_depart : int) : 

# fonctionnelle mais à tester avec la base de donnée


    """cherche les kayaks à ramasser et renvoie les horaires de ramassage et leur nombre"""
    #cur.execute(f"SELECT nb_2places, parcours, h_depart, min_depart FROM location WHERE nb_2places > 0 AND a_depart = {a_depart} AND m_depart = {m_depart} AND j_depart = {j_depart} ORDER BY h_depart, min_depart")
    #rows = cur.fetchall() # liste des enregistrements avec un 2 place
    rows = [(3, 0, 14, 55), (1, 1, 13, 1)] # temporaire pour test sans base de donnée

    ramassage0 = [(12 + i, 30) for i in range(6)]
    ramassage1 = [(13 + i, 0) for i in range(6)]

    parcours0 = []
    parcours1 = []
    for i in range(len(rows)): # tableaux avec les horaires d'arrivée pour chaque parcours
        row = list(rows[i])
        row[2] += 3 + row[1]
        if row[1] == 0 :
            parcours0.append(rows[i])
        else :
            parcours1.append(rows[i])
        
    #sorted(parcours0, key=lambda x: (x[2], x[3])) # a supprimer si tout fonctionne bien
    #sorted(parcours1, key=lambda x: (x[2], x[3])) 

    j = 0
    dict_parcours0 = {k:0 for k in range(len(ramassage0))}
    i = 0
    while i < len(parcours0):
        if parcours0[i][2:4] <= ramassage0[j]:
            dict_parcours0[j] += parcours0[i][0]
            i += 1
        else :
            j += 1

    resultat0 = [ramassage0[k] + (dict_parcours0[k],) for k in range(len(ramassage0))] 


    j = 0
    dict_parcours1 = {k:0 for k in range(len(ramassage0))}
    i = 0
    while i < len(parcours1):
        if parcours1[i][2:4] <= ramassage1[j]:
            dict_parcours1[j] += parcours1[i][0]
            i += 1
        else :
            j += 1
            dict_parcours1[j] = 0
    resultat1 = [ramassage1[k] + (dict_parcours1[k],) for k in range(len(ramassage1))]

    return (resultat0, resultat1) # de la forme ([facile], [avancé])
    # chaque 3-uplets : (heure, minute, nb_kayaks à ramasser)

print(retour_kayaks2places(12,1,2026))



def retour_kayaks1place(j_depart : int, m_depart : int, a_depart : int) :
    # copier la structure de retour_kayaks2places()
    cur.execute(f"SELECT nb_1place, parcours, h_depart, min_depart FROM location WHERE nb_1place > 0 AND a_depart = {a_depart} AND m_depart = {m_depart} AND j_depart = {j_depart}")
    rows = cur.fetchall() # liste des enregistrements avec un 2 place

    return resultat0, resultat1 # de la forme ([facile], [avancé])
    # chaque 3-uplets : (heure, minute, nb_kayaks à ramasser)
    
def kayak_dispo(j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int, nb_2places : int, parcours : int) -> bool :
    cur.execute(f"""SELECT nb_1place FROM location WHERE j_depart = {j_depart} AND m_depart = {m_depart} AND a_depart = {a_depart} 
                AND h_depart > {h_depart-parcours} AND h_depart+{parcours} < {h_depart+parcours} AND min_depart = {min_depart}""")
        #min_depart doit probablement être modifiée comme h_depart, j'ai un peu de mal à voir comment pour l'instant
        # je comprend pas où tu veux aller mais c'est sûrement faux
    




# j'ai essayé de trouver une méthode pour guider ton travail ---->



    cur.execute(f"""SELECT SUM(nb_1place) FROM location WHERE j_depart = {j_depart} AND m_depart = {m_depart} AND a_depart = {a_depart} 
                AND (h_depart < {h_depart} OR (h_depart = {h_depart} AND min_depart = {min_depart}))""")
    # on selectionne toutes les resa kayak une place et les somme
    # Donc 50 - cette somme = nb de kayak dispo sans ceux qui vont etre ramenés
    # c'est là où il faut utiliser retour_kayaks1place pour savoir combien de kayak vont etre ramenés avant l'heure de la nouvelle resa






    used_1 = cur.fetchall()
    #rassemble tous les kayaks 1 place utilisés durant le moment donné en entrée.
    cur.execute(f"""SELECT nb_2place FROM location WHERE j_depart = {j_depart} AND m_depart = {m_depart} AND a_depart = {a_depart} 
                AND h_depart > {h_depart-parcours} AND h_depart+{parcours} < {h_depart+parcours} AND min_depart = {min_depart}""")
    used_2 = cur.fetchall()
    #dessous, observe si on peut utiliser les kayaks demandés en +.
    if len(used_1)+nb_1place < 51 and len(used_2)+nb_2places<51:
        return True
    else:
        return False
        
        
#creer_base(9,00,18,00,50,50) #Création de la base de données en fonction des consignes.
#date(14, 1, 2026)
#jour_suivant()
#ajoute_resa(17, 1, 2026, 12, 30, 1, 1, 0, ajouter_client('Porlier', 'Baptiste'))

con.commit()
con.close()


