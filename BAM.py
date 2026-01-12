from sqlite3 import *

con = connect("BAM.db")
cur = con.cursor()



def create_base(h_ouverture : int, min_ouverture : int, h_fermeture : int, min_fermeture : int, nb_1place : int, nb_2places : int) -> None:
<<<<<<< HEAD
    
    cur.execute("DROP TABLE date") # empêche plusieurs enregistrements

    cur.execute("""CREATE TABLE IF NOT EXISTS date(
                annee INT,
                mois INT,
                jour INT
                )""")
    
    '''cur.execute("""CREATE TABLE IF NOT EXISTS kayak(
                id_kayak INT PRIMARY KEY,
                type INT
                )""")'''
    
    cur.execute("""CREATE TABLE IF NOT EXISTS location(
            id_location INT PRIMARY KEY AUTO_INCREMENT,
            a_depart INT,
            m_depart INT,
            j_depart INT,
            h_depart INT,
            min_depart INT,
            parcours INT,
            nb_1place INT,
            nb_2places INT
            )""")            # id_kayak INT REFERENCES kayak(id_kayak)
=======
>>>>>>> a27f4c84c5976915bd3f88f9dd18d62dc34ac633
    
    cur.execute("PRAGMA foreign_keys = ON") # Activer les clés étrangères
    
    # --- Empêche plusieurs enregistrements ---
    cur.execute("DROP TABLE IF EXISTS retour_kayak")
    cur.execute("DROP TABLE IF EXISTS location")
    cur.execute("DROP TABLE IF EXISTS kayak")
    cur.execute("DROP TABLE IF EXISTS nb_kayak")
    cur.execute("DROP TABLE IF EXISTS parcours")
    cur.execute("DROP TABLE IF EXISTS employe")
    cur.execute("DROP TABLE IF EXISTS client")
    cur.execute("DROP TABLE IF EXISTS date")
    
    # --- Création de la table date ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS date(
        annee INT,
        mois INT,
        jour INT
        )
    """)
    # --- Création de la table kayak ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS kayak(
        id_kayak INTEGER PRIMARY KEY AUTOINCREMENT,
        type INT REFERENCES nb_kayak(type),
        etat TEXT
        )
    """)
    
    # --- Création de la table location ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS location(
        id_location INTEGER PRIMARY KEY AUTOINCREMENT,
        id_kayak INT REFERENCES kayak(id_kayak),
        id_parcours INT REFERENCES parcours(id_parcours),
        id_client INT REFERENCES client(id_client),
        date DATE,
        heure_debut TIME,
        heure_fin TIME,
        heure_retour TIME,
        )
    """)
    #Les dates sont de la forme : année-mois-jour
    #Les heures sont de la forme : xx:xx
    
    # --- Création de la table client ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS client(
        id_client INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        prenom TEXT,
        reservation BOOLEAN
        )
    """)
    
    # --- Création de la table parcours ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parcours(
        id_parcours INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_parcours TEXT,
        distance INT,
        depart TEXT,
        arrivee TEXT
        )
    """)
    
    # --- Création de la table nbkayak ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nbkayak(
        type TEXT INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre INT
        )       
    """)
    cur.execute("INSERT INTO date VALUES (2026,1,12)")
    
    # --- Création de la table employe ---
    cur.execute("""
    CREATE TABLE
        )      
    """)


def id_kayak_insert():
    cur.executemany("INSERT INTO kayak VALUES (?)", [(i, 1) for i in range(1,51)])
    cur.executemany("INSERT INTO kayak VALUES (?)", [(i, 2) for i in range(51,101)])



def date(j : int,  m : int, a : int) -> None :
    cur.executemany("UPDATE table SET (?)", [(j, m, a)])


def jour_suivant() -> tuple[int, int, int] :
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

def ajoute_resa(j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int) -> None :
    #verif si c possible
    cur.execute("SELECT * FROM date")
    
    if cur.fetchone() <= (a_depart, m_depart, j_depart) : # verif si la date est plus petite qua la date de la résa
        ... #ajoute si possible 
    #cur.execute("INSERT INTO gnagngna ")
    

def supprime_resa(j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int):
    # si resa est plus ancienne que la date -> on ne peut pas supprimer

    # sinon  : cur.execute("DEL ...")
    cur.execute("SELECT * FROM date")
    
    if cur.fetchone() <= (a_depart, m_depart, j_depart) : # verif si la date est plus petite qua la date de la résa
        ...



# On considère que l'employé commence à 12h30 par aller au point le plus proche, parcours facile, 0
def retour_kayaks2places(j_depart : int, m_depart : int, a_depart : int) : 
    cur.execute(f"SELECT nb_2places, parcours, h_depart, min_depart FROM location WHERE nb_2places > 0, a_depart = {a_depart} AND m_depart = {m_depart} AND j_depart = {j_depart}")
    rows = cur.fetchall() # liste des enregistrements avec un 2 place

    ramassage0 = [(12 + i, 30) for i in range(6)]
    ramassage1 = [(13 + i, 0) for i in range(6)]

    parcours = []
    for i in range(len(rows)): # tableau avec les horaires d'arrivée
        rows[i][2] += 3 + rows[i][1]
        if rows[i][1] == 0 :
            parcours[0].append(rows[i])
        else :
            parcours[1].append(rows[i])
        
    sorted(parcours[0], key=lambda x: (x[2], x[3])) # tri par heure et minute peut-etre à optimiser ou a faire nous meme
    sorted(parcours[1], key=lambda x: (x[2], x[3])) 

    j = 0
    dict_parcours0 = {k:0 for k in range(len(ramassage0))}
    for i in range(len(parcours[0])):
        if parcours[0][i][2:3] <= ramassage0[j]:
            dict_parcours0[j] += 1
        else :
            j += 1
    resultat0 = [ramassage0[k] + (dict_parcours0[k],) for k in range(len(ramassage0))]


    j = 0
    dict_parcours1 = {k:0 for k in range(len(ramassage1))}
    for i in range(len(parcours[1])):
        if parcours[1][i][2:3] <= ramassage1[j]:
            dict_parcours1[j] += 1
        else :
            j += 1
    resultat1 = [ramassage1[k] + (dict_parcours1[k],) for k in range(len(ramassage1))]

    return (resultat0, resultat1) # de la forme ([facile], [avancé])
    # chaque 3-uplets : (heure, minute, nb_kayaks à ramasser)

def retour_kayaks1place(j_depart : int, m_depart : int, a_depart : int) :
    # copier la structure de retour_kayaks2places()
    ...



con.commit()
con.close()
