from sqlite3 import *

con = connect("BAM.db")
cur = con.cursor()

def create_base(h_ouverture : int, min_ouverture : int, h_fermeture : int, min_fermeture : int, nb_1place : int, nb_2places : int) -> None:
    
    cur.execute("PRAGMA foreign_keys = ON") # Activer les clés étrangères
    
    # --- Empêche plusieurs enregistrements ---
    tables = ['retour_kayak', 'location', 'kayak', 'nb_kayak', 'parcours', 'employe', 'client', 'date']
    for e in tables :
        cur.execute(f"DROP TABLE IF EXISTS {e}")
    
    # --- Création de la table date ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS date(
        annee INT,
        mois INT,
        jour INT
        )
    """)

    
    # --- Création de la table location --- Il faut une table kayak où chaque kayak a un id et un type(simple ou double). Ca n'a pas de sens de le mettre dans une table location.
    # La table location sert a savoir quel client (table client)  loue quoi (table kayak). Ces attributs auraient du sens dans une table 'boutique de location'.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS location(
        id_location INTEGER PRIMARY KEY AUTOINCREMENT,
        nb_1place INT,
        nb_2places INT,
        parcours INT,
        id_client INT REFERENCES client(id_client),
        a_depart INT,
        m_depart INT,
        j_depart INT,
        h_depart INT,
        min_depart INT
        )
    """)
    
    #Les dates sont de la forme : année-mois-jour
    #Les heures sont de la forme : xx:xx 
    # On travail avec des int sur chaques valeurs pour effectuer des comparaisons plus facilement avec les dates et heures stockées et passées en argument
    
    # --- Création de la table client ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS client(
        id_client INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        prenom TEXT,
        reservation BOOLEAN -------------- est ce que c'est vrm utile ?
        )
    """)
    
    
    '''# --- Création de la table nbkayak ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nbkayak(
        type TEXT PRIMARY KEY,
        nombre INT CHECK (nombre <= 50)
        )       
    """)'''
    cur.execute("INSERT INTO date VALUES (2026,1,12)")
    

    # --- Création de la table retour_kayak --------------------- c pas utle vu qu'on le calcule
    '''cur.execute("""
    CREATE TABLE IF NOT EXISTS retour_kayak(
        id_retour INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        heure TIME,
        id_employe INT
        FOREIGN KEY (id_employe) REFERENCES employe(id_employe),
        fin_parcours TEXT,
        nb_de_kayak INT CHECK (nb_de_kayak <= 12)
        )        
    """)'''


    con.commit()




def id_kayak_insert():
    """surement pas utile mais c okay"""
    cur.executemany("INSERT INTO kayak VALUES (?)", [(i, 1) for i in range(1,51)])
    cur.executemany("INSERT INTO kayak VALUES (?)", [(i, 2) for i in range(51,101)])
    con.commit()



def date(j : int,  m : int, a : int) -> None :
    """update date dans la base de donnée"""
    cur.executemany("UPDATE table SET (?)", [(j, m, a)])
    con.commit()


def jour_suivant() -> tuple[int, int, int] :
    """trouver la date suivante de celle stockée dans la base de donnée"""
    cur.execute("SELECT * FROM date")
    a, m, j = cur.fetchone()
    
        #if m==2 alors verifier année bissxtile
    if a % 4 == 0 :
        if m in [1,3,5,7,8,10,12]:
            max_j=31
        elif m==2 :
            max_j=29
        else :
            max_j=30
    else:
        if m in [1,3,5,7,8,10,12]:
            max_j=31
        elif m==2 :
            max_j=28
        else :
            max_j=30
    
    if max_j == j : # ou <= j pour si une valeur de date est corrompue dès l'arrivée
        j = 1
        if m == 12 :
            m = 1
            a += 1
        else :
            m +=1
    else :
        j += 1
    
    print(a,m,j)
    
    return (a, m ,j)

#jour_suivant()

def ajoute_resa(j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int, nb_2places : int, parcours : int, id_client) -> bool :
    """cherche si la résa est possible, si oui ajoute la résa"""
    check = kayak_dispo(j_depart, m_depart, a_depart, h_depart, min_depart, nb_1place, nb_2places, parcours)
    #check contient True si la réservation est possible.
    if check :
        #verif si c possible
        cur.execute("SELECT * FROM date")
        if cur.fetchone() <= (a_depart, m_depart, j_depart) : # verif si la date est plus petite qua la date de la résa
            """On compare pas les heures ? C'est parce que l'heure est pas dans 'date' ?
            non c juste que c pas le but ici, on veut juste pas reserver pour une date passée, et je te rappelle qu'on a pas accès à l'heure actuelle dans la base de donnée
            """
            #ajoute si possible
            cur.execute(f"""INSERT INTO location VALUES ({nb_1place},{nb_2places},{parcours},{id_client},
                                                        {a_depart},{m_depart},{j_depart},{h_depart},{min_depart})""") # l'id_location est attribué automatiquement
            con.commit()
            return True # On return True si la réservation a été faite
    else:
        return False # On return False si la réservation n'est pas possible

    

def supprime_resa(id_location : int, j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int):
    """supprime une résa si elle est possible à supprimer"""
    # si resa est plus ancienne que la date -> on ne peut pas supprimer

    # sinon  : cur.execute("DEL ...")
    cur.execute("SELECT * FROM date")
    
    if cur.fetchone() <= (a_depart, m_depart, j_depart) : # verif si la date est plus petite qua la date de la résa
        cur.execute(f"DELETE FROM location WHERE id_location ={id_location}")
        con.commit()



# On considère que l'employé commence à 12h30 par aller au point le plus proche, parcours facile, 0
def retour_kayaks2places(j_depart : int, m_depart : int, a_depart : int) : 
    """cherche les kayaks à ramasser et renvoie les horaires de ramassage et leur nombre"""
    #cur.execute(f"SELECT nb_2places, parcours, h_depart, min_depart FROM location WHERE nb_2places > 0 AND a_depart = {a_depart} AND m_depart = {m_depart} AND j_depart = {j_depart} ORDER BY h_depart, min_depart")
    #rows = cur.fetchall() # liste des enregistrements avec un 2 place
    rows = [(3, 0, 12, 30), (1, 1, 13, 0)] # temporaire pour test sans base de donnée

    ramassage0 = [(12 + i, 30) for i in range(6)]
    ramassage1 = [(13 + i, 0) for i in range(6)]

    parcours0 = []
    parcours1 = []
    for i in range(len(rows)): # tableau avec les horaires d'arrivée
        rows[i][2] += 3 + rows[i][1]
        if rows[i][1] == 0 :
            parcours0.append(rows[i])
        else :
            parcours1.append(rows[i])
        
    #sorted(parcours0, key=lambda x: (x[2], x[3])) # tri par heure et minute peut-etre à optimiser ou a faire nous meme
    #sorted(parcours1, key=lambda x: (x[2], x[3])) 

    j = 0
    dict_parcours0 = {j:0}
    i = 0
    while i < len(parcours0):
        if parcours0[i][2:3] <= ramassage0[j]:
            dict_parcours0[j] += 1
            i += 1
        else :
            j += 1
            dict_parcours0[j] = 0
    resultat0 = [ramassage0[k] + (dict_parcours0[k],) for k in range(len(ramassage0))]


    j = 0
    dict_parcours1 = {k:0 for k in range(len(ramassage1))}
    for i in range(len(parcours1)):
        if parcours1[i][2:3] <= ramassage1[j]:
            dict_parcours1[j] += 1
        else :
            j += 1
    resultat1 = [ramassage1[k] + (dict_parcours1[k],) for k in range(len(ramassage1))]

    return (resultat0, resultat1) # de la forme ([facile], [avancé])
    # chaque 3-uplets : (heure, minute, nb_kayaks à ramasser)





def retour_kayaks1place(j_depart : int, m_depart : int, a_depart : int) :
    # copier la structure de retour_kayaks2places()
    cur.execute(f"SELECT nb_1place, parcours, h_depart, min_depart FROM location WHERE nb_1place > 0 AND a_depart = {a_depart} AND m_depart = {m_depart} AND j_depart = {j_depart}")
    rows = cur.fetchall() # liste des enregistrements avec un 2 place

    return (resultat0, resultat1) # de la forme ([facile], [avancé])
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



con.commit()
con.close()
