import tkinter as tk
from tkinter import ttk
import json

class VolleyballApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Volleyball Match Analysis")

        # Dropdown menu options
        matches = ["1", "2", "3"]
        sets = ["1", "2", "3"]
        names = ["NULL", "DIDI", "ELLIOT", "FELIX", "LEO", "MAXIME", "XIANG", "THIERRY"]
        results = ["NULL", "BON", "NEUTRE", "NUL"]
        targets = ["NULL", "CIBLE 1", "CIBLE 2", "CIBLE 3", "CIBLE 4", "CIBLE 5", "CIBLE 6"]

        # Data storage
        self.data = {}

        # Create main frame
        main_frame = tk.Frame(self)
        main_frame.pack(padx=20, pady=20)

        # Labels and Dropdowns
        self.match_combo = self.create_dropdown(main_frame, "Match N°", matches, 0, column=0)
        self.set_combo = self.create_dropdown(main_frame, "Set", sets, 0, column=1)
        self.set_combo.bind("<<ComboboxSelected>>", self.reset_scores)  # Bind event for set change
        self.create_score_row(main_frame, "Score", 1)
        self.service_combos = self.create_action_row(main_frame, "Service", names, results, targets, 2)
        self.create_reception_counter(main_frame, 3)
        self.block_combos = self.create_action_row(main_frame, "Block", names, results, targets, 4)
        self.reception_combos = self.create_action_row(main_frame, "Réception", names, results, targets, 5)
        self.passe_combos = self.create_action_row(main_frame, "Passe", names, results, targets, 6)
        self.attaque_combos = self.create_action_row(main_frame, "Attaque", names, results, targets, 7)

        export_button = tk.Button(main_frame, text="Exporter les données", command=self.save_data)
        export_button.grid(row=8, column=0, columnspan=6, pady=10)  # Adjust row and column as needed


    def create_dropdown(self, frame, label_text, options, row, column):
        label = tk.Label(frame, text=label_text)
        label.grid(row=row, column=column * 2, padx=(10, 20), pady=10, sticky='e')
        combo = ttk.Combobox(frame, values=options, width=10)
        combo.grid(row=row, column=column * 2 + 1, padx=(0, 20), pady=10, sticky='w')
        combo.current(0)
        return combo

    def create_score_row(self, frame, label_text, row):
        label = tk.Label(frame, text=label_text)
        label.grid(row=row, column=0, padx=(10, 20), pady=10, sticky='e')

        # Score for our team
        self.our_score = tk.IntVar(value=0)

        decrement_our_score = tk.Button(frame, text="-", command=lambda: self.update_score(self.our_score, -1))
        decrement_our_score.grid(row=row, column=1, padx=(0, 20), pady=10, sticky='w')

        our_score_label = tk.Label(frame, textvariable=self.our_score, width=5)
        our_score_label.grid(row=row, column=2, padx=(0, 10), pady=10, sticky='w')

        increment_our_score = tk.Button(frame, text="+", command=lambda: self.update_score(self.our_score, 1))
        increment_our_score.grid(row=row, column=3, padx=(0, 10), pady=10, sticky='w')

        # Score for opponent team
        self.opponent_score = tk.IntVar(value=0)

        decrement_opponent_score = tk.Button(frame, text="-", command=lambda: self.update_score(self.opponent_score, -1))
        decrement_opponent_score.grid(row=row, column=4, padx=(0, 20), pady=10, sticky='w')

        opponent_score_label = tk.Label(frame, textvariable=self.opponent_score, width=5)
        opponent_score_label.grid(row=row, column=5, padx=(0, 10), pady=10, sticky='w')

        increment_opponent_score = tk.Button(frame, text="+", command=lambda: self.update_score(self.opponent_score, 1))
        increment_opponent_score.grid(row=row, column=6, padx=(0, 10), pady=10, sticky='w')

    def update_score(self, score_var, increment, is_reception_count=False):
        current_score = score_var.get()
        new_score = current_score + increment
        if new_score >= 0:  # Prevent negative scores
            # Save data
            match = self.get_match()
            set = self.get_set()
            our_score = self.our_score.get()
            opponent_score = self.opponent_score.get()
            reception_count = self.reception_count.get()
            
            self.save_data()

            #change score
            score_var.set(new_score)

            #reset
            self.reset_actions()
            if not is_reception_count:
                self.reset_actions(True)     

            if match not in self.data:
                self.data[match] = {}
            if set not in self.data[match]:
                self.data[match][set] = {}

            if not is_reception_count:
                self.reception_count.set(1)

            
    def reset_actions(self, reset_service=False):
        match = self.get_match()
        set = self.get_set()
        our_score = str(self.our_score.get())
        opponent_score = str(self.opponent_score.get())
        score = str(self.our_score.get()) + ":" + str(self.opponent_score.get())
        reception = self.get_reception_count()

        if score in self.data[match][set] and reception in self.data[match][set][score]:
            self.block_combos[0].set(self.data[match][set][score]["Block"]["name"])
            self.block_combos[1].set(self.data[match][set][score]["Block"]["result"])
            self.block_combos[2].set(self.data[match][set][score]["Block"]["target"])
            self.reception_combos[0].set(self.data[match][set][score]["Reception"]["name"])
            self.reception_combos[1].set(self.data[match][set][score]["Reception"]["result"])
            self.reception_combos[2].set(self.data[match][set][score]["Reception"]["target"])
            self.passe_combos[0].set(self.data[match][set][score]["Passe"]["name"])
            self.passe_combos[1].set(self.data[match][set][score]["Passe"]["result"])
            self.passe_combos[2].set(self.data[match][set][score]["Passe"]["target"])
            self.attaque_combos[0].set(self.data[match][set][score]["Attaque"]["name"])
            self.attaque_combos[1].set(self.data[match][set][score]["Attaque"]["result"])
            self.attaque_combos[2].set(self.data[match][set][score]["Attaque"]["target"])
        else:
            self.block_combos[0].set("NULL")
            self.block_combos[1].set("NULL")
            self.block_combos[2].set("NULL")
            self.reception_combos[0].set("NULL")
            self.reception_combos[1].set("NULL")
            self.reception_combos[2].set("NULL")
            self.passe_combos[0].set("NULL")
            self.passe_combos[1].set("NULL")
            self.passe_combos[2].set("NULL")
            self.attaque_combos[0].set("NULL")
            self.attaque_combos[1].set("NULL")
            self.attaque_combos[2].set("NULL")

        if reset_service:
            if score in self.data[match][set] and reception in self.data[match][set][score]:
                self.service_combos[0].set(self.data[match][set][score]["Service"]["name"])
                self.service_combos[1].set(self.data[match][set][score]["Service"]["result"])
                self.service_combos[2].set(self.data[match][set][score]["Service"]["target"])
            else:
                self.service_combos[0].set("NULL")
                self.service_combos[1].set("NULL")
                self.service_combos[2].set("NULL")


    def create_reception_counter(self, frame, row):
        label = tk.Label(frame, text="Nombre de Réceptions")
        label.grid(row=row, column=0, padx=(10, 20), pady=10, sticky='e')

        self.reception_count = tk.IntVar(value=0)

        decrement_reception = tk.Button(frame, text="-", command=lambda: self.update_score(self.reception_count, -1, True))
        decrement_reception.grid(row=row, column=1, padx=(0, 20), pady=10, sticky='w')

        reception_label = tk.Label(frame, textvariable=self.reception_count, width=5)
        reception_label.grid(row=row, column=2, padx=(0, 10), pady=10, sticky='w')

        increment_reception = tk.Button(frame, text="+", command=lambda: self.update_score(self.reception_count, 1, True))
        increment_reception.grid(row=row, column=3, padx=(0, 10), pady=10, sticky='w')

    def create_action_row(self, frame, action, names, results, targets, row):
        label = tk.Label(frame, text=action)
        label.grid(row=row, column=0, padx=(10, 20), pady=10, sticky='e')

        name_combo = ttk.Combobox(frame, values=names, width=10)
        name_combo.grid(row=row, column=1, padx=(0, 20), pady=10, sticky='w')
        name_combo.current(0)
        name_combo.bind("<<ComboboxSelected>>", lambda e, combo=name_combo: self.update_action_row(combo, results, targets))

        result_label = tk.Label(frame, text=f"{action} Résultat")
        result_label.grid(row=row, column=2, padx=(10, 20), pady=10, sticky='e')

        result_combo = ttk.Combobox(frame, values=results, width=10)
        result_combo.grid(row=row, column=3, padx=(0, 20), pady=10, sticky='w')
        result_combo.current(0)
        result_combo.configure(state="readonly")

        target_label = tk.Label(frame, text=f"{action} Cible")
        target_label.grid(row=row, column=4, padx=(10, 20), pady=10, sticky='e')

        target_combo = ttk.Combobox(frame, values=targets, width=10)
        target_combo.grid(row=row, column=5, padx=(0, 20), pady=10, sticky='w')
        target_combo.current(0)
        target_combo.configure(state="readonly")

        # Store references to result and target comboboxes
        name_combo.result_combo = result_combo
        name_combo.target_combo = target_combo

        return name_combo, result_combo, target_combo

    def update_action_row(self, name_combo, results, targets):
        if name_combo.get() == "NULL":
            name_combo.result_combo.set("NULL")
            name_combo.target_combo.set("NULL")
        else:
            name_combo.result_combo.set(results[0])
            name_combo.target_combo.set(targets[0])

    def get_match(self):
        return self.match_combo.get()

    def get_set(self):
        return self.set_combo.get()

    def get_reception_count(self):
        return self.reception_count.get()

    def get_action_data(self, action_combos):
        name = action_combos[0].get()
        result = action_combos[1].get()
        target = action_combos[2].get()
        return {"name": name, "result": result, "target": target}

    def save_data(self):
        match = self.get_match()
        set = self.get_set()
        if match not in self.data:
            self.data[match] = {}
        if set not in self.data[match]:
            self.data[match][set] = {}

        score = str(self.our_score.get()) + ":" + str(self.opponent_score.get())

        if score not in self.data[match][set]:
            self.data[match][set][score] = {}

        self.data[match][set][score]['Service'] = self.get_action_data(self.service_combos)
        
        reception = self.get_reception_count()
        if reception not in self.data[match][set][score]:
            self.data[match][set][score][reception] = {}

        self.data[match][set][score][reception]['Block'] = self.get_action_data(self.block_combos)
        self.data[match][set][score][reception]['Reception'] = self.get_action_data(self.reception_combos)
        self.data[match][set][score][reception]['Passe'] = self.get_action_data(self.passe_combos)
        self.data[match][set][score][reception]['Attaque'] = self.get_action_data(self.attaque_combos)


        with open('sheet_volleyball_data.json', 'w') as file:
            json.dump(self.data, file, indent=4)

    def load_data(self):
        try:
            with open('volleyball_data.json', 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}

    def reset_scores(self, event):
        self.our_score.set(0)
        self.opponent_score.set(0)

if __name__ == "__main__":
    app = VolleyballApp()
    app.mainloop()

