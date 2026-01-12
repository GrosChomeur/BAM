from sqlite3 import *

con = connect("BAM.db")


cur = con.cursor()



def create_base(h_ouverture : int, min_ouverture : int, h_fermeture : int, min_fermeture : int, nb_1place : int, nb_2places : int) -> None:
    cur.execute("DROP TABLE date") # empêche plusieurs enregistrements
    cur.execute("""CREATE TABLE IF NOT EXISTS date(
                annee INT,
                mois INT,
                jour INT
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS kayak(
                id_kayak INT PRIMARY KEY,
                type INT
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS location(
            id_location INT PRIMARY KEY AUTO_INCREMENT,
            type INT,
            id_kayak INT REFERENCES kayak(id_kayak)
            )""")
    
    
    
    cur.execute("INSERT INTO date VALUES (2026,1,12)")
    


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

    #cur.execute("INSERT INTO gnagngna ")
    ...

def supprime_resa(j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int):
    #si resa est plus ancienne que la date -> on ne peut pas supprimer
    #sinon  : cur.execute("DEL ...")
    ...


def retour_kayaks2places(j_depart : int, m_depart : int, a_depart : int) :
    #récupérer la difficulté puis évaluer le temps de trajet et l'ajouter à l'heure de départ 
    ...

def retour_kayaks1place(j_depart : int, m_depart : int, a_depart : int) :
    #récupérer la difficulté puis évaluer le temps de trajet et l'ajouter à l'heure de départ
    ...



con.commit()
con.close()