

import sqlite3
from Bam import creer_base, con, cur

def test_creer_base():
    
    creer_base(9, 0, 18, 0, 50, 50)
    
    cur.execute("""SELECT * FROM boutique_location""")
    resultat = cur.fetchone()
    #Cas normal
    assert resultat == (9, 0, 18, 0, 50, 50), 'Pas ok'
    print("✓")
    #cas où nb de kayaks négatif
    try : 
        assert resultat == (9, 0, 18, 0, 50, -50), 'Pas ok'
        print("✓")
    except:
        print("Pa s ok")
        
    #
    try : 
        assert resultat == (18, 0, 9, 0, 50, 50), 'Pas ok'
        print("✓")
    except:
        print("Pas ok")
        
if __name__ == "__main__":
    try:
        test_creer_base()
    finally:
        con.close()
