class ModeManager:
    def __init__(self):
        self.show_vision = False
        self.show_targets = False
        self.show_current = False

        self.show_temp_map = False
        self.show_oxygen_map = False

        self.creative = False
        self.cre_plankton = False
        self.cre_crustacean = False
        self.cre_fish = False
        self.cre_del = False

        self.active_modes = []
    
    def toggle_mode(self, mode, text):
        setattr(self, mode, not getattr(self, mode))

        if getattr(self, mode):
            if text == 'Temp Map' and 'Oxy Map' in self.active_modes:
                self.active_modes.remove('Oxy Map')
                self.show_oxygen_map = False
            elif text == 'Oxy Map' and 'Temp Map' in self.active_modes:
                self.active_modes.remove('Temp Map')
                self.show_temp_map = False

            elif text == 'Creative' and 'Oxy Map' in self.active_modes:
                self.active_modes.remove('Oxy Map')
                self.show_oxygen_map = False
            
            elif text == 'Creative' and 'Temp Map' in self.active_modes:
                self.active_modes.remove('Temp Map')
                self.show_temp_map = False
            
            elif text == 'Creative' and 'Targets' in self.active_modes:
                self.active_modes.remove('Targets')
                self.show_targets = False
            
            if text == 'Plankton' and 'Crustacean' in self.active_modes:
                self.active_modes.remove('Crustacean')
                self.cre_crustacean = False
            
            elif text == 'Plankton' and 'Fish' in self.active_modes:
                self.active_modes.remove('Fish')
                self.cre_fish = False
            
            if text == 'Crustacean' and 'Plankton' in self.active_modes:
                self.active_modes.remove('Plankton')
                self.cre_plankton = False
            
            elif text == 'Crustacean' and 'Fish' in self.active_modes:
                self.active_modes.remove('Fish')
                self.cre_fish = False
            
            if text == 'Fish' and 'Plankton' in self.active_modes:
                self.active_modes.remove('Plankton')
                self.cre_plankton = False
            
            elif text == 'Fish' and 'Crustacean' in self.active_modes:
                self.active_modes.remove('Crustacean')
                self.cre_crustacean = False

            if text not in self.active_modes:
                self.active_modes.append(text)
        else:
            if text in self.active_modes:
                self.active_modes.remove(text)
            
            if 'Creative' not in self.active_modes and 'Plankton' in self.active_modes:
                self.active_modes.remove('Plankton')
                self.cre_plankton = False
            
            elif 'Creative' not in self.active_modes and 'Crustacean' in self.active_modes:
                self.active_modes.remove('Crustacean')
                self.cre_crustacean = False
            
            elif 'Creative' not in self.active_modes and 'Fish' in self.active_modes:
                self.active_modes.remove('Fish')
                self.cre_fish = False
            
            if 'Creative' not in self.active_modes and 'Deleting' in self.active_modes:
                self.active_modes.remove('Deleting')
                self.cre_del = False