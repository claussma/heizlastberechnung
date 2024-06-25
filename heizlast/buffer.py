import pandas as pd

class BufferTank:
    def __init__(self, capacity_liters: float, initial_temp: float, min_temp: float, max_temp: float):
        """
        Initialisiert den Pufferspeicher.
        :param capacity_liters: Kapazität des Pufferspeichers in Litern.
        :param initial_temp: Anfangstemperatur des Pufferspeichers in °C.
        :param min_temp: Minimale Temperatur des Pufferspeichers in °C.
        :param max_temp: Maximale Temperatur des Pufferspeichers in °C.
        """
        self.capacity_liters = capacity_liters
        self.capacity_kwh = self.capacity_liters * 4.186 / 3600  # Kapazität in kWh (4.186 kJ/kg°C und 1 Liter Wasser wiegt 1 kg)
        self.current_temp = initial_temp
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.charge = (self.current_temp - self.min_temp) * self.capacity_kwh / (self.max_temp - self.min_temp)
    
    def add_energy(self, energy: float):
        """
        Fügt Energie dem Pufferspeicher hinzu.
        :param energy: Energie in kWh.
        """
        self.charge = min(self.capacity_kwh, self.charge + energy)
        self.update_temperature()
    
    def draw_energy(self, energy: float) -> float:
        """
        Entnimmt Energie aus dem Pufferspeicher.
        :param energy: Angeforderte Energie in kWh.
        :return: Tatsächlich entnommene Energie in kWh.
        """
        if self.charge >= energy:
            self.charge -= energy
            self.update_temperature()
            return energy
        else:
            available_energy = self.charge
            self.charge = 0
            self.update_temperature()
            return available_energy
    
    def update_temperature(self):
        """
        Aktualisiert die aktuelle Temperatur des Pufferspeichers basierend auf dem Ladezustand.
        """
        self.current_temp = self.min_temp + self.charge * (self.max_temp - self.min_temp) / self.capacity_kwh
