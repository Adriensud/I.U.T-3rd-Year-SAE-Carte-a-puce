import mysql.connector
import smartcard.System as scardsys
import smartcard.util as scardutil
import smartcard.Exceptions as scardexcp

# Assurez-vous de remplacer les valeurs de connexion par les vôtres
cnx = mysql.connector.connect(user='root',
                              password='root',
                              host='localhost',
                              database='purpledragon')

def print_hello_message():
    print("-------------------------------------------------")
    print("-- Logiciel embarqué sur la borne de recharge --")
    print("-------------------------------------------------")

def print_menu():
    print("1 - Afficher mes informations")
    print("2 - Consulter mes bonus")
    print("3 - Transférer mes bonus sur ma carte")
    print("4 - Consulter le crédit disponible sur ma carte")
    print("5 - Recharger avec ma carte bancaire")
    print("6 - Quitter")

def afficher_informations(etu_num):
    sql = "SELECT * FROM Etudiant WHERE etu_num = %s;"
    val = (etu_num,)
    cursor = cnx.cursor()
    cursor.execute(sql, val)
    row = cursor.fetchone()
    if row:
        print(row)
    else:
        print("Aucun étudiant trouvé avec ce numéro.")

def consulter_bonus(etu_num):
    sql = "SELECT * FROM Compte WHERE etu_num = %s AND type_opeartion = 'Bonus';"
    val = (etu_num,)
    cursor = cnx.cursor()
    cursor.execute(sql, val)
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def transferer_bonus(etu_num):
    sql_select = "SELECT * FROM Compte WHERE etu_num = %s AND type_opeartion = 'Bonus';"
    sql_update = "UPDATE compte SET type_opeartion = 'Bonus transféré' WHERE etu_num = %s AND type_opeartion = 'Bonus';"
    val = (etu_num,)
    cursor = cnx.cursor()
    cursor.execute(sql_select, val)
    bonuses = cursor.fetchall()
    if bonuses:
        cursor.execute(sql_update, val)
        cnx.commit()
        print("Bonus transférés avec succès.")
    else:
        print("Aucun bonus à transférer.")

def consulter_credit():
    # Ici, nous devons construire et envoyer une commande APDU à la carte pour lire le solde
    # L'instruction pour lire le solde est '0x01' dans la classe '0x82'
    apdu = [0x82, 0x01, 0x00, 0x00, 0x02]  # '0x02' est la longueur des données attendues (le solde est un uint16_t)

    try:
        # Envoi de la commande APDU à la carte et réception de la réponse
        data, sw1, sw2 = conn_reader.transmit(apdu)
        if sw1 == 0x90 and sw2 == 0x00:  # Vérification du statut de réponse
            solde = int.from_bytes(data, byteorder='big')  # Convertir les données en nombre
            print(f"Solde actuel sur la carte: {solde} centimes")
        else:
            print(f"Erreur lors de la lecture du solde de la carte: SW1 = {sw1}, SW2 = {sw2}")
    except Exception as e:
        print(f"Erreur lors de la communication avec la carte: {e}")

    else:
        print("Aucune information de crédit disponible.")

def lire_solde_db(etu_num):
    sql = "SELECT SUM(opr_montant) as total_bonus FROM Compte WHERE etu_num = %s AND type_operation = 'Bonus';"
    val = (etu_num,)
    cursor = cnx.cursor()
    cursor.execute(sql, val)
    result = cursor.fetchone()
    return result[0] if result else 0

def recharger_carte(etu_num):
    # Lire le solde de la base de données
    solde_db = lire_solde_db(etu_num)  # Implémentez cette fonction pour lire le solde de la base de données

    # Convertir le solde en format approprié pour la carte (par exemple, en bytes)
    solde_bytes = solde_db.to_bytes(2, byteorder='big')  # Supposons que le solde est un uint16_t

    # Construire la commande APDU pour mettre à jour le solde sur la carte
    # Supposons que l'instruction pour écrire le solde est '0x02' dans la classe '0x82'
    apdu = [0x82, 0x02, 0x00, 0x00] + list(solde_bytes)

    try:
        # Envoi de la commande APDU à la carte et réception de la réponse
        sw1, sw2 = conn_reader.transmit(apdu)
        if sw1 == 0x90 and sw2 == 0x00:  # Vérification du statut de réponse
            print(f"Solde de la carte mis à jour: {solde_db} centimes")
        else:
            print(f"Erreur lors de la mise à jour du solde de la carte: SW1 = {sw1}, SW2 = {sw2}")
    except Exception as e:
        print(f"Erreur lors de la communication avec la carte: {e}")

def main():
    print_hello_message()
    etu_num = input("Veuillez entrer votre numéro étudiant pour commencer: ")  # Simule la lecture de la carte à puce
    while True:
        print_menu()
        choice = input("Choix : ")
        if choice == '1':
            afficher_informations(etu_num)
        elif choice == '2':
            consulter_bonus(etu_num)
        elif choice == '3':
            transferer_bonus(etu_num)
        elif choice == '4':
            consulter_credit(etu_num)
        elif choice == '5':
            recharger_credit()
        elif choice == '6':
            print("Merci d'avoir utilisé le logiciel Berlicum. À bientôt !")
            break
        else:
            print("Choix non valide, veuillez réessayer.")

if __name__ == "__main__":
    main()