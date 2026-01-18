import sqlite3
from BAM2 import (creer_base, con, cur, date, jour_suivant, ajouter_client, ajoute_resa, supprime_resa, retour_kayaks1place, retour_kayaks2places)

def test_creer_base():
    print("\nTests de la fonction creer_base() :")
    
    # Cas normal du projet
    print("Test cas normal : ", end = "")
    creer_base(9, 0, 18, 0, 50, 50)
    
    cur.execute("""SELECT * FROM boutique_location""")
    resultat = cur.fetchone()
    assert resultat == (9, 0, 18, 0, 50, 50), '✕\n'
    print('✓\n')
    
    # Cas où nb de kayaks négatif
    print("Test où le nombre de kayak est négatif : ", end = "")
    try : 
        creer_base(9, 0, 18, 0, -50, -50)
        print("✕\n")
    except :
        print('✓\n')
        
    # Cas ou l'heure d'ouverture est après l'heure de fermeture
    print("Test où  l'heure d'ouverture est après l'heure de fermeture: ", end = "")
    try : 
        creer_base(18, 0, 9, 0, 50, 50)
        print('✕\n')
    except:
        print('✓\n')

        

def test_jour_suivant():

    print("\nTests de la fonction jour_suivant() :\n")
    creer_base(9, 0, 18, 0, 50, 50)

    # Cas normal
    date(10, 1, 2026)
    nouveau_jour = jour_suivant()
    print("Test passage au jour suivant normal :")
    try:
        assert nouveau_jour == (11, 1, 2026), '✕\n'
        print('✓\n')
    except :
        print('✕\n')
    
    #Cas ou passage au mois suivant
    date(31, 1, 2026)
    nouveau_jour = jour_suivant()
    print("Test passage au mois suivant" , end = "")
    try :
        assert nouveau_jour == (1, 2, 2026), '✕\n'
        print('✓\n')
    except :
        print('✕\n')
        
    #Cas Année bissextile
    date(28, 2, 2028)
    nouveau_jour = jour_suivant()
    print("Test année bissextille", end ="")
    try :
        assert nouveau_jour == (29, 2, 2028), '✕\n'
        print('✓\n')
    except :
        print('✕\n')

def test_ajouter_client():
    print("\nTests de la fonction ajouter_client() :")
    
    client1 = ajouter_client("test@mail.com", "Lorem", "Ipsum")
    assert client1 is True, "Le client est déjà dans la base de données."
    
    print("Test si on essaye d'ajouter un client deja présent : ", end = "")
    client2 = ajouter_client("test@mail.com", "Lorem", "Ipsum")
    try :
        assert client2 is False, '✕\n'
        print('✓\n')
    except :
        print('✕\n')

def test_ajoute_resa():
    print("\nTests de la fonction ajoute_resa() :")
    
    creer_base(9, 0, 18, 0, 50, 50)
    ajouter_client("test2@mail.com", "Lorem", "Ipsum")
    date(1, 1, 2026)

    # Cas réservation valide
    print("Tests réservation normale : ", end = "")
    try:
        ajoute_resa(10, 1, 2026, 10, 0, 2, 0, 0, "test2@mail.com")                 # 10 janvier 10h réservation de 2 kayaks 1 place
                                                                                   # On vérifie qu'une réservation a bien été ajoutée pour ces paramètres
        cur.execute("""SELECT count(*) FROM location WHERE email = 'test2@mail.com' AND j_depart = 10 AND m_depart = 1 AND a_depart = 2026 AND h_depart = 10 AND min_depart = 0 AND nb_1place = 2 AND nb_2places = 0 AND parcours = 0""") 
        assert cur.fetchone()[0] == 1, '✕\n'
        print('✓\n')
    except:
        print('✕\n')

    #Cas heure interdite (Parcours 10km après ou à 14h par exemple)
    print("Test réservation parcours 1 après 14h : ", end = "")
    try:
        ajoute_resa(10, 1, 2026, 15, 30, 1, 0, 1, "test2@mail.com")
        cur.execute("""SELECT count(*) FROM location WHERE h_depart = 15 AND min_depart = 30 AND parcours = 1""")
        assert cur.fetchone()[0] == 0, '✕\n'
        print('✓\n')
    except:
        print('✕\n')

    # Cas dépassement stock

    # Cas on a un nouveau stock car retour de kayak

def test_supprime_resa():
    print("\nTests de la fonction supprime_resa() ---")
    
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
        assert cur.fetchone()[0] == 0, '✕\n'
        print('✓\n')
    except:
        print('✕\n')
        
def test_retour_kayaks():
    print("\nTests des fonctions de retour de kayaks :")
    creer_base(9, 0, 18, 0, 50, 50)
    ajouter_client("test4@retours.com", "Nom", "Prenom")
    date(1, 1, 2026)

    ajoute_resa(2, 1, 2026, 9, 0, 5, 10, 0, "test4@retours.com") # Réservation de 5 kayaks 1 place et 10 kayaks 2 places
    
    res1 = retour_kayaks1place(1, 1, 2026)
    res2 = retour_kayaks2places(1, 1, 2026)
    
    #Test retour 1 place
    print("Test calcul retour 1 place : ", end = "")
    try:
        assert res1[0][0][2] == 5, '✕\n'
        print('✓\n')
    except:
        print('✕\n')

    #Test retour 2 places
    print("Test calcul retour 2 places: ", end = "")
    try:
        assert res2[0][0][2] == 10, '✕\n'
        print('✓\n')
    except:
        print('✕\n')


        
if __name__ == "__main__":
    try:
        test_creer_base()
        test_jour_suivant()
        test_ajouter_client()
        test_ajoute_resa()
        test_supprime_resa()
        test_retour_kayaks()
        print("Tests terminés avec succès")
    finally:
        con.close()
