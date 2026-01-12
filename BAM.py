from sqlite3 import *

con = connect("BAM.db")


cur = con.cursor()

def create_base(h_ouverture : int, min_ouverture : int, h_fermeture : int, min_fermeture : int, nb_1place : int, nb_2places : int) -> None:
    cur.execute("CREATE TABLE boutique()")
    ...

def date(j : int,  m : int, a : int) -> None :
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
    
    if max_j == j :
        j = 1
    else :
        j += 1

    if m==12 :
        a += 1
        m = 1
    
    cur.execute("UPDATE table SET (?,?,?)", (j, m, a))


def jour_suivant() -> (int, int, int) :
    ...

def ajoute_resa(j_depart : int, m_depart : int, a_depart : int, h_depart : int, min_depart : int, nb_1place : int)