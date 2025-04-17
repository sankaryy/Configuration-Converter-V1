import ldap3
import hashlib
import json
from datetime import datetime, timedelta



login_cache={}

falid_login={}






def login_check(falid_login,user_ip):
    if user_ip in falid_login:
        if "block_time" in falid_login[user_ip]:
            if falid_login[user_ip]["block_time"] < datetime.now():
                falid_login.pop(user_ip)
            else:
                return False
        else:
            return True
    else:
        return True

    
def local_authentication(username,password):
    with open("authentication.json") as auth:
        authentication=auth.read()
    
    auth=json.loads(authentication)

    if username in auth:
        if auth[username]==password:
            return True
        else:
            return False
    else:
        return False


    




def hashing (plain_text):
    hash_object = hashlib.sha256(plain_text.encode('utf-8'))  
    hex_dig = hash_object.hexdigest()
    return hex_dig




def ldap(username,password,server_ip):
    expiry_Time=datetime.now()+timedelta(hours=24)
    server = ldap3.Server(server_ip)
    connection = ldap3.Connection(server, authentication=ldap3.NTLM,user=f'{server}\\{username}', password=f'{password}')
    if connection.bind():
        connection.unbind()
        login_cache.update({hashing(username):{"password":hashing(password),"expiry_Time":expiry_Time}})
        return True
    else:
        connection.unbind()
        return False




    

























    









    

    


    


