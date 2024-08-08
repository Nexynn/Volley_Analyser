import json
import pandas as pd

# Charger les données JSON depuis le fichier
with open('sheet_volleyball_data.json', 'r') as f:
    data = json.load(f)

# Préparer une structure de données pour les statistiques
stats = {}
scores = {}
collective_scores = {}

# Fonction pour convertir les résultats en scores
def convert_result_to_score(result, action="NULL"):
    if action == "Reception":
        bon = 3
        neutre = -1
        mauvais = -3
    elif action == "Passe":
        bon = 2
        neutre = -1
        mauvais = -3
    elif action == "Attaque":
        bon = 4
        neutre = 1
        mauvais = -2
    elif action == "Block":
        bon = 3
        neutre = 1
        mauvais = -3
    else:
        bon = 2
        neutre = 1
        mauvais = -1

    if result == "BON":
        return bon
    elif result == "NEUTRE":
        return neutre
    elif result == "MAUVAIS":
        return mauvais
    else:
        return 0

# Fonction pour évaluer les passes et les attaques selon les réceptions et les passes associées
def evaluate_collective_score(previous_result, current_result, current_action):
    if current_action == "Passe" or current_action == "Attaque":
        if previous_result == "BON":
            if current_result in ["NEUTRE", "MAUVAIS"]:
                return convert_result_to_score(current_result, current_action) - 1
            else:
                return convert_result_to_score(current_result, current_action)
        elif previous_result == "NEUTRE":
            if current_result == "BON":
                return convert_result_to_score(current_result, current_action) + 1
            elif current_result == "MAUVAIS":
                return convert_result_to_score(current_result, current_action) - 1
            else:
                return convert_result_to_score(current_result, current_action)
        elif previous_result == "MAUVAIS":
            if current_result in ["BON", "NEUTRE"]:
                return convert_result_to_score(current_result, current_action) + 1
            else:
                return convert_result_to_score(current_result, current_action)
    
    return convert_result_to_score(current_result)

def save():
    # Convertir les statistiques en DataFrame
    stats_df = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index': 'Name'})
    scores_df = pd.DataFrame.from_dict(scores, orient='index').reset_index().rename(columns={'index': 'Name'})
    collective_scores_df = pd.DataFrame.from_dict(collective_scores, orient='index').reset_index().rename(columns={'index': 'Name'})

    # Lire le fichier Excel existant
    excel_path = 'excel_volleyball_stats.xlsx'

    try:
        # Lire les feuilles existantes
        existing_data = pd.read_excel(excel_path, sheet_name=None)
    
        # Calculer la nouvelle position de départ (2 lignes en dessous des données existantes)
        new_startrow_stats = existing_data['Statistiques'].shape[0] + 2
        new_startrow_scores = existing_data['Scores'].shape[0] + 2
        new_startrow_collective = existing_data['Collective Scores'].shape[0] + 2
    
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            # Écrire les nouvelles données deux lignes en dessous des données existantes
            stats_df.to_excel(writer, sheet_name='Statistiques', index=False, startrow=new_startrow_stats, header=False)
            scores_df.to_excel(writer, sheet_name='Scores', index=False, startrow=new_startrow_scores, header=False)
            collective_scores_df.to_excel(writer, sheet_name='Collective Scores', index=False, startrow=new_startrow_collective, header=False)
        
    except FileNotFoundError:
        # Si le fichier n'existe pas, créer un nouveau fichier et y écrire les données
        with pd.ExcelWriter(excel_path) as writer:
            stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
            scores_df.to_excel(writer, sheet_name='Scores', index=False)
            collective_scores_df.to_excel(writer, sheet_name='Collective Scores', index=False)
    stats.clear()
    scores.clear()
    collective_scores.clear()


# Parcourir les données JSON pour collecter les statistiques
for match, sets in data.items():
    for set_num, points in sets.items():
        for score, actions in points.items():
            # Initialisation des résultats précédents pour évaluer les passes et les attaques
            for action, details in actions.items():
                previous_results = {"Reception": "NULL", "Passe": "NULL"}
                if action == "Service":
                    if details["name"] != "NULL":
                        if details["name"] not in stats:
                            stats[details["name"]] = {"Service": 0, "Reception": 0, "Passe": 0, "Attaque": 0, "Block": 0}
                            scores[details["name"]] = {"Service": 0, "Reception": 0, "Passe": 0, "Attaque": 0, "Block": 0}
                            collective_scores[details["name"]] = {"Service": 0, "Reception": 0, "Passe": 0, "Attaque": 0, "Block": 0}
                        stats[details["name"]]["Service"] += 1
                        scores[details["name"]]["Service"] += convert_result_to_score(details["result"])
                        collective_scores[details["name"]]["Service"] += convert_result_to_score(details["result"])
                        
                elif isinstance(details, dict):
                    for sub_action, sub_details in details.items():
                        if sub_details["name"] != "NULL":
                            if sub_details["name"] not in stats:
                                stats[sub_details["name"]] = {"Service": 0, "Reception": 0, "Passe": 0, "Attaque": 0, "Block": 0}
                                scores[sub_details["name"]] = {"Service": 0, "Reception": 0, "Passe": 0, "Attaque": 0, "Block": 0}
                                collective_scores[sub_details["name"]] = {"Service": 0, "Reception": 0, "Passe": 0, "Attaque": 0, "Block": 0}
                            stats[sub_details["name"]][sub_action] += 1
                            scores[sub_details["name"]][sub_action] += convert_result_to_score(sub_details["result"], sub_action)

                            # Evaluation collective des passes et des attaques
                            if sub_action in ["Passe", "Attaque"]:
                                previous_action = "Reception" if sub_action == "Passe" else "Passe"
                                previous_result = previous_results[previous_action]
                                current_result = sub_details["result"]
                                collective_scores[sub_details["name"]][sub_action] += evaluate_collective_score(previous_result, current_result, sub_action)
                                if (sub_action == "Passe"):
                                    previous_results["Passe"] = sub_details["result"]
                            else:
                                if (sub_action == "Reception"):
                                    previous_results["Reception"] = sub_details["result"]
                                collective_scores[sub_details["name"]][sub_action] += convert_result_to_score(sub_details["result"], sub_action)
        save()


print("Les statistiques ont été exportées vers excel_volleyball_stats.xlsx")

