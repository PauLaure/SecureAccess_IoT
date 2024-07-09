from web3 import Web3
import hashlib
import time
from paho.mqtt import client as mqtt_client
import create_database
from email_handler import send_email
from random import randint
import config
import ssl

web3 = Web3(Web3.HTTPProvider(config.provider_url))  # Assicurati di modificare l'URL del provider se necessario

# Imposta l'account da utilizzare per interagire con il contratto
web3.eth.defaultAccount = config.default_account  # Sostituisci con l'indirizzo del tuo account Ethereum


# Crea l'istanza del contratto
contract_instance = web3.eth.contract(address=config.contract_address, abi=config.contract_abi)


broker = config.broker
port = config.port

topic_out = config.topic_out
topic_in = config.topic_in
topic_otp = config.topic_otp
topic_alert = config.topic_alert

count = 0
timer = 0
otp = 0
utente = None  # Aggiunto per mantenere il riferimento all'utente per la gestione dell'OTP
user_table = {}

# Definisci all_users come variabile globale
users = create_database.allUsers()
all_users = [user[0] for user in users]  
 
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    
    #ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #ssl_context.load_verify_locations(cafile=config.CA_CERT)
    #ssl_context.load_cert_chain(certfile= "./solc/ca1/server.pem", keyfile= "./solc/ca1/server.key")
    client = mqtt_client.Client("Arduino_to_server001")
    client.on_connect = on_connect
    
    #client.tls_set(ca_certs="./solc/ca1/server.pem", 
    #               certfile= config.CERTFILE, 
    #               keyfile= config.KEYFILE, 
    #               cert_reqs=ssl.CERT_NONE, 
    #               tls_version=ssl.PROTOCOL_TLS, 
    #               ciphers=None)
    
    client.connect(broker, port)
    return client

def verify(password, timer, otp):
    if timer != 0: 
        if time.time() < timer:
            if otp == int(password):
                return True
        print("tempo scaduto")
    else:
        print("timer non settato")
    return False


def generate_sha(user):
    data = f"{user}-{int(time.time())}"
    sha = hashlib.sha256()
    sha.update(data.encode())
    user_sha = sha.hexdigest()
    user_sha = "0x" + user_sha
    if user in user_table:
        user_table[user].append(user_sha)
    else:
        user_table[user] = [user_sha]
    return user_sha

def get_users_from_sha(user_sha):
    # Ottiene gli utenti corrispondenti alla SHA-256 dalla tabella di corrispondenza
    users = []
    for user, shas in user_table.items():
        if user_sha in shas:
            users.append(user)
            return users
    return ["Utente non trovato"]

def register_action(user, action):
    user_sha = generate_sha(user)

    # Costruisce la transazione
    tx = contract_instance.functions.registerAction(user_sha, action).build_transaction({
        'from': web3.eth.defaultAccount,  # Utilizza l'account predefinito per la transazione
        'gas': 2000000,  # Specifica il gas necessario per la transazione
        'gasPrice': web3.to_wei('50', 'gwei')  # Specifica il prezzo del gas
    })

    # Invia la transazione
    tx_hash = web3.eth.send_transaction(tx)

    # Attendere la conferma della transazione
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    # Ritorna il risultato della transazione
    return tx_receipt

def on_message(client, userdata, msg):
    global count, timer, otp, utente
    password = msg.payload.decode()
    print(f"Topic `{msg.topic}` : Received `{msg.payload.decode()}` ")

    if msg.topic == "server":
        print("Server is connected")
        
    elif msg.topic == topic_in:
        while count <= 3:
            utente = create_database.search_user_by_private_key(password)
            password= ""
            if utente is not None:
                otp = randint(100000, 999999)
                timer = time.time() + 60
                send_email(utente, 'Codice OTP', f'Il tuo codice OTP: {otp}, hai 60 secondi per inserirlo')
                print(f"Topic `{msg.topic}`: inviato codice OTP a {utente}")
                tx= register_action(utente, "OTP")
                print(f"Transazione registrata: {tx}")
                count = 0
                break
            else:
                count += 1
                client.publish(topic_out, "No_Match")
                print(f"Topic `{topic_out}`: Published `No_Match`")
                break
        if count >= 3:
            client.publish(topic_alert, "Tentato accesso non autorizzato")
            print(f"Topic `{topic_alert}`: Published `Tentato accesso non autorizzato`")
            send_email(all_users, 'Messaggio di allerta', "Tentato accesso non autorizzato")
            tx= register_action("all", "Tentato accesso")
            print(f"Transazione registrata: {tx}")
            count=0
            
    elif msg.topic == topic_otp:
        password= msg.payload.decode()
        while count <= 3:
            if verify(password, timer, otp):
                client.publish(topic_out, "Match")
                print(f"Topic `{topic_out}`: Published `Match`")
                tx= register_action(utente, "Match")
                print(f"Transazione registrata: {tx}")
                count = 0
                break
            else:
                count += 1
                client.publish(topic_out, "No_Match")
                print(f"Topic `{topic_out}`: Published `No_Match`")
                break
            
        if count >= 3:
            client.publish(topic_alert, "Tentativi otp esauriti")
            print(f"Topic `{topic_alert}`: Published `Tentativi otp esauriti`")
            send_email(utente, 'Messaggio di allerta', "Tentativi otp esauriti, reinserire il codice identificativo per ricevere un nuovo OTP")
            tx= register_action(utente, "No Match")
            print(f"Transazione registrata: {tx}")
            count=0
            utente = None
            otp = 0
            timer = 0
    else:
        # Invia email di allerta a tutti gli utenti nel database
        send_email(all_users, 'Messaggio di allerta', "topic sconosciuto o server sotto attacco")
        tx= register_action("all", "Alert attacco")
        print(f"Transazione registrata: {tx}")
        # Pubblica il messaggio di allerta sul topic di allerta MQTT
        client.publish(topic_alert, "topic sconosciuto o server sotto attacco")
        print(f"Topic `{topic_alert}`: Published `topic sconosciuto o server sotto attacco`")

def subscribe(client):
    client.subscribe(topic_in)
    client.subscribe(topic_otp)
    client.on_message = on_message

def run(client):
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    client = connect_mqtt()
    run(client)
    
