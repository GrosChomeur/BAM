import sqlite3
from Bam import (creer_base, con, cur, date, jour_suivant, ajouter_client, ajoute_resa, supprime_resa)

def test_creer_base():
    print("Tests de la fonction creer_base() :")
    creer_base(9, 0, 18, 0, 50, 50)
    
    cur.execute("""SELECT * FROM boutique_location""")
    resultat = cur.fetchone()
    
    #Cas normal
    print("Test cas normal : ", end = "")
    assert resultat == (9, 0, 18, 0, 50, 50), '✕'
    print('✓')
    
    #Cas où nb de kayaks négatif
    print("Test où le nombre de kayak est négatif : ", end = "")
    try : 
        assert resultat == (9, 0, 18, 0, 50, -50), '✕'
        print(" ✓")
    except:
        print('✕')
        
    #Cas ou l'heure d'ouverture est après l'heure de fermeture
    print("Test où  l'heure d'ouverture est après l'heure de fermeture: ", end = "")
    try : 
        assert resultat == (18, 0, 9, 0, 50, 50), '✕'
        print('✓')
    except:
        print('✕')
        
def test_jour_suivant():
    print("Tests de la fonction jour_suivant() :")
    
    #Cas normal
    date(10, 1, 2026)
    nouveau_jour = jour_suivant()
    print("Test passage au jour suivant normal :")
    try:
        assert nouveau_jour == (11, 1, 2026), '✕'
        print('✓')
    except :
        print('✕')
    
    #Cas ou passage au mois suivant
    date(31, 1, 2026)
    nouveau_jour = jour_suivant()
    print("Test passage au mois suivant" , end = "")
    try :
        assert nouveau_jour == (1, 2, 2026), '✕'
        print('✓')
    except :
        print('✕')
        
    #Cas Année bissextile
    date(28, 2, 2028)
    nouveau_jour = jour_suivant()
    print("Test année bissextille", end ="")
    try :
        assert nouveau_jour == (29, 2, 2028), '✕'
        print('✓')
    except :
        print('✕')

def test_ajouter_client():
    print("Tests de la fonction ajouter_client() :")
    
    client1 = ajouter_client("test@mail.com", "Lorem", "Ipsum")
    assert client1 is False, "Le client ne devrait pas exister"
    
    print("Test si on essayer d'ajouter un client deja présent : ", end = "")
    client2 = ajouter_client("test@mail.com", "Lorem", "Ipsum")
    try :

        assert client2 is True, '✕'
        print('✓')
    except :
        print('✕')

def test_ajoute_resa():
    print("Tests de la fonction ajoute_resa() :")
    
    creer_base(9, 0, 18, 0, 50, 50)
    ajouter_client("test2@mail.com", "Lorem", "Ipsum")
    date(1, 1, 2026)

    #Cas réservation valide
    print("Tests réservation normale : ", end = "")
    try:
        ajoute_resa(10, 1, 2026, 10, 0, 2, 0, 0, "test2@mail.com")
        cur.execute("""SELECT count(*) FROM location WHERE email = 'test2@mail.com'""")
        assert cur.fetchone()[0] == 1, '✕'
        print('✓')
    except:
        print('✕')

    #Cas heure interdite (Parcours 10km après 14h par exemple)
    print("Test réservation parcours 1 après 14h : ", end = "")
    try:
        ajoute_resa(10, 1, 2026, 15, 0, 1, 0, 1, "test2@mail.com")
        cur.execute("""SELECT count(*) FROM location WHERE h_depart = 15""")
        assert cur.fetchone()[0] == 0, '✕'
        print('✓')
    except:
        print('✕')

def test_supprime_resa():
    print("Tests de la fonction supprime_resa() ---")
    
    creer_base(9, 0, 18, 0, 50, 50)
    ajouter_client("test2@mail.com", "Lorem", "Ipsum")
    date(1, 1, 2026)
    
    ajoute_resa(20, 1, 2026, 10, 0, 1, 0, 0, "test2@mail.com")
    cur.execute("""SELECT id_location FROM location LIMIT 1""")
    id_loc = cur.fetchone()[0]

    print("Test suppression réservation future : ", end = "")
    try:
        supprime_resa(id_loc, 20, 1, 2026, 10, 0, 1)
        cur.execute("""SELECT count(*) FROM location WHERE id_location = ?""", (id_loc,))
        assert cur.fetchone()[0] == 0, '✕'
        print('✓')
    except:
        print('✕')
        
if __name__ == "__main__":
    try:
        test_creer_base()
        test_jour_suivant()
        test_ajouter_client()
        test_ajoute_resa()
        test_supprime_resa()
        print("Tests terminés avec succès")
    finally:
        con.close()
