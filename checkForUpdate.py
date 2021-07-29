from motorrad import *
from subprocess import run

f_links = ''
webRemote = motorradWeb()
webLocal  = motorradWeb()
webRemote.loadLinksFromWeb()
webLocal.loadLinksFromFile()
links_changed = (webRemote.links != webLocal.links)
if links_changed:
    f_links = webRemote.dumpLinksToFile()
    print("Links have changed, Check {}".format(f_links))

f_db = ''
dbRemote = motorradDB()
dbLocal  = motorradDB()
dbRemote.loadFromUrls(webRemote.links)
dbLocal.loadFromFile()
db_changed = (dbRemote != dbLocal)
if db_changed:
    f_db = dbRemote.dumpToFile()
    print("Database has changed, Check {}".format(f_db))

if links_changed or db_changed:
    shall = input("Update reference files? [y/N] ").lower() == 'y'
    if shall and links_changed:
        run(["cp", f_links,"motorrad_links.json"])
        pass
    if shall and db_changed:
        run(["cp", f_db, "motorrad_db.json"])
        pass

run(["ls","-l"])
