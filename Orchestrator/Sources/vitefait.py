from Gotham_link_BDD import add_link_DB

db_settings = {"username":"gotham", "password":"password", "hostname":"192.168.1.172", "port":"3306", "database":"GOTHAM"}
lk_infos = {"id":"lk-1B5B3A1E32EE11EBB1F25E22FC2CA667", "nb_hp": 4, "nb_serv": 2, "port": 66, "tag_hp":"OpenSSH,SSH,Elasticsearch", "tag_serv":"Europe,Suisse,Geneve"}

print(add_link_DB(db_settings, lk_infos))