class AppState:
    def __init__(self):
        self.nav_mode_active = False
        self.last_output = ""
        self.is_speaking = False

    def toggle_nav_mode(self):
        self.nav_mode_active = not self.nav_mode_active
        return self.nav_mode_active

    def set_last_output(self, text):
        self.last_output = text

# Global singleton state
state = AppState()
