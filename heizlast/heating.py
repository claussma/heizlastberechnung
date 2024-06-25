import pandas as pd

from .buffer import *


class HeatingSystem:
    pass

class HeatingSystemGas(HeatingSystem):
    def __init__(self, name: str, efficiency: float, max_power: float):
        """
        Initialisiert ein Heizungssystem.
        :param name: Name des Heizungssystems.
        :param efficiency: Effizienz des Heizungssystems (zwischen 0 und 1).
        :param max_power: Maximale Heizleistung des Heizungssystems in kW.
        """
        self.name = name
        self.efficiency = efficiency
        self.max_power = max_power  # in kW

    def provide_energy(self, energy_needed: float) -> float:
        """
        Bereitstellung der Heizenergie durch das Heizungssystem.
        :param energy_needed: Benötigte Energie in kWh.
        :return: Tatsächlich bereitgestellte Energie in kWh.
        """
        energy_provided = min(energy_needed, self.max_power)
        return energy_provided * self.efficiency

class HeatingSystemSolar:
    def __init__(self, name: str, efficiency: float, module_power_wp: float, num_modules: int,  module_area: float: 2.0):
        """
        Initialisiert das Solarheizungssystem.
        :param name: Name des Heizungssystems.
        :param efficiency: Effizienz des Heizungssystems.
        :param module_power_wp: Leistung eines Solarmoduls in Wp.
        :param num_modules: Anzahl der Solarmodule.
        """
        self.name = name
        self.module_power_wp = module_power_wp
        self.num_modules = num_modules
        self.efficiency = efficiency
        self.module_area = module_area

    def provide_energy(self, solar_radiation: float) -> float:
        """
        Berechnet die bereitgestellte Solarenergie in kWh basierend auf der Globalstrahlung.
        :param solar_radiation: Globalstrahlung in W/m².
        :return: Bereitgestellte Solarenergie in kWh.
        """
        # Gesasmtfläche
        total_area = self.module_area * self.num_modules
        
        # Gesamtleistung der Module in Wp
        total_power_wp = self.module_power_wp * total_area / 1000 #kWp
        # Berechnung der Solarenergie in kWh
        solar_energy_kwh = total_power_wp * solar_radiation * self.efficiency
        return solar_energy_kwh

    
class MultiHeatingSystem:
    def __init__(self, buffer_tank: BufferTank, systems: list):
        """
        Initialisiert das Multi-Heizungssystem.
        :param buffer_tank: Instanz des Pufferspeichers.
        :param systems: Liste der Heizungssysteme (mit Priorität).
        """
        self.buffer_tank = buffer_tank
        self.systems = systems

    def operate_heating(self, energy_needed_series: pd.Series, solar_radiation_series: pd.Series) -> pd.DataFrame:
        """
        Simuliert die Heizungssteuerung für eine Serie von Energiebedarfswerten.
        :param energy_needed_series: Serie von Energiebedarfswerten in kWh.
        :param solar_radiation_series: Serie von Globalstrahlung in W/m².
        :return: DataFrame mit tatsächlich bereitgestellten Heizenergiewerten in kWh für jedes Heizungssystem.
        """
        results = {
            'time': energy_needed_series.index,
            'energy_needed': energy_needed_series,
            'buffer_energy': [],
            'provided_energy': []
        }

        for system in self.systems:
            results[system.name] = []

        for timestamp, energy_needed in energy_needed_series.items():
            energy_from_buffer = self.buffer_tank.draw_energy(energy_needed)
            energy_deficit = energy_needed - energy_from_buffer
            results['buffer_energy'].append(energy_from_buffer)
            
            for system in self.systems:
                energy_provided = 0
                if isinstance(system, HeatingSystemSolar):
                    solar_radiation = solar_radiation_series[timestamp]
                    energy_provided = system.provide_energy(solar_radiation)
                    if energy_deficit > 0:
                        energy_provided = min(energy_provided, energy_deficit)
                else:
                    if energy_deficit > 0:
                        energy_provided = system.provide_energy(energy_deficit)
                
                if energy_provided > 0:
                    self.buffer_tank.add_energy(energy_provided)
                    energy_deficit -= energy_provided

                results[system.name].append(energy_provided)

            provided_energy = energy_needed - energy_deficit
            results['provided_energy'].append(provided_energy)

        return pd.DataFrame(results).set_index('time')
