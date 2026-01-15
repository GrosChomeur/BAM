import sqlite3
from BAM import creer_base

con = sqlite3.connect("BAM.db")
cur = con.cursor()
#con = sqlite3.connect("BAM.db")
#(h_ouverture : int, min_ouverture : int, h_fermeture : int, min_fermeture : int, nb_1place : int, nb_2places : int) -> None:
def test_creer_base() :

    creer_base(9, 0, 18, 0, 50, -50)
    
    cur.execute("""SELECT * FROM boutique_location""")
    a = cur.fetchone()
    assert a == (h_ouv, m_ouv, h_ferm, m_ferm, nb1, nb2), 'Null'

test_creer_base()
con.close()
