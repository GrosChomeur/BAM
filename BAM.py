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

def id_kayak_insert():
    """surement pas utile mais c okay"""
    cur.executemany("INSERT INTO kayak VALUES (?)", [(i, 1) for i in range(1,51)])
    cur.executemany("INSERT INTO kayak VALUES (?)", [(i, 2) for i in range(51,101)])



def date(j : int,  m : int, a : int) -> None :
    """update date dans la base de donnée"""
    cur.executemany("UPDATE table SET (?)", [(j, m, a)])


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

def ajoute_resa(j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int, parcours : int, nb_1place : int, nb_2places : int) -> None :
    """cherch si la résa est possible, si oui ajoute la résa"""
    cur.execute(f"SELECT * FROM location WHERE j_depart = {j_depart} AND m_depart = {m_depart} AND a_depart = {a_depart} AND h_depart = {h_depart} AND min_depart = {min_depart}")
    # ^ un début de truc on peut le virer
    #verif si c possible
    cur.execute("SELECT * FROM date")
    
    if cur.fetchone() <= (a_depart, m_depart, j_depart) : # verif si la date est plus petite qua la date de la résa
        """On compare pas les heures ? C'est parce que l'heure est pas dans 'date' ?"""
        #ajoute si possible
        cur.execute(f"INSERT INTO location VALUES ({creer id location??},{nb_1place},{nb_2places},{parcours},{id_client},
                                                    {a_depart},{m_depart},{j_depart},{h_depart},{min_depart})")
    #cur.execute("INSERT INTO gnagngna ")
    

def supprime_resa(id_location : int, j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int):
    """supprime une résa si elle est possible à supprimer"""
    # si resa est plus ancienne que la date -> on ne peut pas supprimer

    # sinon  : cur.execute("DEL ...")
    cur.execute("SELECT * FROM date")
    
    if cur.fetchone() <= (a_depart, m_depart, j_depart) : # verif si la date est plus petite qua la date de la résa
        cur.execute(f"DELETE FROM location WHERE id_location ={id_location}")



# On considère que l'employé commence à 12h30 par aller au point le plus proche, parcours facile, 0
def retour_kayaks2places(j_depart : int, m_depart : int, a_depart : int) : 
    """cherche les kayaks à ramasser et renvoie les horaires de ramassage et leur nombre"""
    cur.execute(f"SELECT nb_2places, parcours, h_depart, min_depart FROM location WHERE nb_2places > 0 AND a_depart = {a_depart} AND m_depart = {m_depart} AND j_depart = {j_depart}")
    rows = cur.fetchall() # liste des enregistrements avec un 2 place

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
        
    sorted(parcours0, key=lambda x: (x[2], x[3])) # tri par heure et minute peut-etre à optimiser ou a faire nous meme
    sorted(parcours1, key=lambda x: (x[2], x[3])) 

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



con.commit()
con.close()
