import requests
import datetime
import urllib3
import tkinter as tk
from tkinter import ttk

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

dayStageNb = [(7,3), (8,4), (9,5), (10,6), (11,7), (12,8), (13,9), (14,10), (16,11), (17,12), (18,13), (19,14), (20,15), (22,16), (23,17), (24,18), (25,19), (26,20), (27,21)]

# The list above contains tuples of (day, stage number) for the Tour de France 2025.
# The first element is the day of the month, and the second element is the stage number
found = False


def get_rider_name(bib, datajson):
    for rider in range(1, len(datajson) - 1):
        if datajson[rider]["bib"] == bib:
            return datajson[rider]["firstname"] + " " + datajson[rider]["lastname"]
        
def get_rider_team(bib, datajson):
    teamId = ""
    for rider in range(1, len(datajson) - 1):
        if datajson[rider]["bib"] == bib:
            teamId = datajson[rider]["_parent"][10:]
            break
    for team in range(1, len(datajson) - 1):
        if datajson[team]["_id"] == teamId:
            return datajson[team]["name"]
            


# Création de la fenêtre principale
root = tk.Tk()
root.title("Gestion des données avec Treeview")



tree = ttk.Treeview(root,columns=("nom", "prenom", "bib"))
tree.heading("nom",text="Nom")
tree.heading("prenom",text="Prénom")
tree.heading("bib",text="Team")
tree.column("nom",width=150,anchor="center")
tree.column("prenom",width=150,anchor="center")
tree.column("bib",width=150,anchor="center")


tree.tag_configure('parentrow', background='lightgrey')


def reload():
    print("call relaod")
    # main
    for i in range(len(dayStageNb)):
        if dayStageNb[i][0] == datetime.datetime.today().day:
            stageNb = str(dayStageNb[i][1])
            found = True
            break

    if found :
        url = "https://racecenter.letour.fr/api/pack-2025-"


        resp = requests.get(url+stageNb, verify=False)
        respJson = resp.json()
        tree.delete(*tree.get_children())

        print(respJson[0]["groups"][0]["name"], end=" : ")
        print(respJson[0]["groups"][0]["remainingDistance"]/1000, end='')
        print("km", end="  (")
        print(len(respJson[0]["groups"][0]["bibs"]), end=" coureurs)\n")
        parent_id = tree.insert("", "end",text=respJson[0]["groups"][0]["name"],values=( str(round(respJson[0]["groups"][0]["remainingDistance"]/1000,1)) + " km","", str(len(respJson[0]["groups"][0]["bibs"])) + " coureurs"), tags = ('parentrow',))
        
        for bib in respJson[0]["groups"][0]["bibs"]:
            riderName = get_rider_name(bib["bib"], respJson)
            if riderName:
                tree.insert(parent_id, "end",text=bib["bib"],values=(riderName.split()[1], riderName.split()[0], get_rider_team(bib["bib"], respJson)))




        for i in range(1, len(respJson[0]["groups"])):
            print(respJson[0]["groups"][i]["name"], end=" : ")
            print("   +", end = "")

            gapTime = respJson[0]["groups"][i]["computedRelative"]
            if gapTime >= 60:
                print(str(gapTime//60) + ":" , end="")
                if gapTime % 60 < 10:
                    print("0" + str(gapTime % 60), end="")
                else:
                    print(str(gapTime % 60), end="")
                print(" min", end=" ")
            else:
                print(str(gapTime), end="")
                print("s", end="")

            gapDist = (respJson[0]["groups"][i]["remainingDistance"] - respJson[0]["groups"][i]["remainingDistance"])/1000
            if gapDist > 1:
                print(" ( + ", end="")
                print(gapDist, end="")
                print("km)", end="")
            elif gapDist > 0:
                print(" ( + ", end="")
                print(gapDist*1000, end="")
                print("m)", end="")

            print("  (", end="")    
            print(len(respJson[0]["groups"][i]["bibs"]), end=" coureurs)\n")

            if(len(respJson[0]["groups"][i]["bibs"]) == 1):
                bib = respJson[0]["groups"][i]["bibs"][0]["bib"]
                riderName = get_rider_name(bib, respJson)
                if riderName:
                    print("  (" + riderName + ")")

            gapTime = respJson[0]["groups"][i]["computedRelative"]
            if gapTime > 60:
                gapTimeStr = str(gapTime//60) + ":" 
                if gapTime % 60 < 10:
                    gapTimeStr  +="0" + str(gapTime % 60)
                else:
                    gapTimeStr  +=str(gapTime % 60)
                gapTimeStr  +=" min"
            else:
                gapTimeStr = str(gapTime) + "s"
            parent_id = tree.insert("", "end",text=respJson[0]["groups"][i]["name"],values=("","+ " + gapTimeStr, str(len(respJson[0]["groups"][i]["bibs"])) + " coureurs"), tags = ('parentrow',))
            for bib in respJson[0]["groups"][i]["bibs"]:
                riderName = get_rider_name(bib["bib"], respJson)
                if riderName:
                    tree.insert(parent_id, "end",text=bib["bib"],values=(riderName.split()[1], riderName.split()[0], get_rider_team(bib["bib"], respJson)))




        resp.close()
    else:
        print("No stage today.")
    root.after(10000, reload)
    

reload()

    # # Placement du Treeview dans la fenêtre
tree.pack(fill=tk.BOTH,expand=True)
# Boucle principale de l'interface graphique
root.mainloop()