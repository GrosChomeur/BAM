

import sqlite3
from Bam import creer_base, con, cur

def test_creer_base():
    print("Tests de la fonction creer_base() :")
    creer_base(9, 0, 18, 0, 50, 50)
    
    cur.execute("""SELECT * FROM boutique_location""")
    resultat = cur.fetchone()
    
    # ---Cas normal---
    
    assert resultat == (9, 0, 18, 0, 50, 50), 'Pas ok'
    print("✓")
    
    # ---Cas où nb de kayaks négatif---
    print("Test 2 : ")
    try : 
        assert resultat == (9, 0, 18, 0, 50, -50), '✕'
        print(" ✓")
    except:
        print("✕")
        
    #---Cas ou l'heure d'ouverture est après l'heure de fermeture---
    print("Test 3 : ", end = "")
    try : 
        assert resultat == (18, 0, 9, 0, 50, 50), '✕'
        print("✓")
    except:
        print("✕")
        
        

if __name__ == "__main__":
    try:
        test_creer_base()
    finally:
        con.close()
