import pandas as pd
import numpy as np

class Layer:
    def __init__(self, name:str, thickness: float, 
                thermal_conductivity: float = None, 
                is_air: bool = False):
        """
        Initialisiert eine Schicht.
        :param thickness: Dicke der Schicht in Metern.
        :param thermal_conductivity: Wärmeleitfähigkeit der Schicht in W/(m*K).
        """
        self.thickness = thickness
        self.thermal_conductivity = thermal_conductivity
        self.is_air = is_air
    
    def r_value(self) -> float:
        """
        Berechnet den R-Wert der Schicht.
        :return: R-Wert in (m²*K)/W.
        """
        if self.is_air:
            air_thermal_conductivity = 0.025  # W/(m*K), stehende Luft
            return self.thickness / air_thermal_conductivity
        else:
            return self.thickness / self.thermal_conductivity

class Wall:
    def __init__(self, name):
        """
        Initialisiert eine Wand mit einer Liste von Schichten.
        """
        self.layers = []
        self.name = name
        
        self.thermal_resistance_inside = 0.0
        self.thermal_resistance_outside = 0.0
        
    def set_thermal_resistance_inside(self, value:float):
        
        self.thermal_resistance_inside = value

    def set_thermal_resistance_outside(self, value:float):
        
        self.thermal_resistance_outside = value
        
    
    def add_layers(self, layers: list):
        """
        Fügt der Wand mehrere Schichten hinzu.
        :param layers: Eine Liste von Instanzen der Klasse Layer.
        """
        self.layers.extend(layers)
    
    def calculate_u_value(self) -> float:
        """
        Berechnet den U-Wert der Wand.
        :return: U-Wert in W/(m²*K).
        """
        total_r_value = sum(layer.r_value() for layer in self.layers)

        total_r_value += self.thermal_resistance_inside
        total_r_value += self.thermal_resistance_outside
        
        return 1 / total_r_value if total_r_value != 0 else float('inf')

class House:
    def __init__(self):
        """
        Initialisiert ein Haus mit einer Liste von Wänden.
        """
        self.components = []
    
    def add_wall(self, name:str, area: float, layers_info: list, 
                thermal_resistance_inside:float = 0.13, 
                thermal_resistance_outside:float = 0.04):
        """
        Fügt dem Haus eine Wand hinzu.
        :param area: Fläche der Wand in Quadratmetern.
        :param layers_info: Eine Liste von Dictionaries, die die Schichten beschreiben.
        """
        layers = [Layer(**info) for info in layers_info]
        wall = Wall(name=name)
        wall.add_layers(layers)
        wall.set_thermal_resistance_inside(thermal_resistance_inside)
        wall.set_thermal_resistance_outside(thermal_resistance_outside)
        
        self.components.append({'name': name, 'area': area, 'structure': wall})
    
    def add_roof(self, area: float, layers_info: list, 
                thermal_resistance_inside:float = 0.1, 
                thermal_resistance_outside:float = 0.1):
        """
        Fügt dem Haus eine Wand hinzu.
        :param area: Fläche der Wand in Quadratmetern.
        :param layers_info: Eine Liste von Dictionaries, die die Schichten beschreiben.
        """
        name = "Dach"
        layers = [Layer(**info) for info in layers_info]
        wall = Wall(name=name)
        wall.add_layers(layers)
        wall.set_thermal_resistance_inside(thermal_resistance_inside)
        wall.set_thermal_resistance_outside(thermal_resistance_outside)
        
        self.components.append({'name': name, 'area': area, 'structure': wall})
    
    def calculate_total_u_value(self) -> float:
        """
        Berechnet den gewichteten durchschnittlichen U-Wert für alle Wände im Haus.
        :return: Durchschnittlicher U-Wert in W/(m²*K).
        """
        total_area = sum(wall['area'] for wall in self.components)
        if total_area == 0:
            return float('inf')  # Falls keine Wände hinzugefügt wurden
        
        weighted_u_sum = sum(component['area'] * component['structure'].calculate_u_value() for component in self.components)
        return weighted_u_sum / total_area
    
    def calc_annual_transmission_heat_loss(self, deltaT = 20.0, hours=24*365) -> float:
        ''' in kWh '''
        
        
        self.annual_transmission_heat_loss = np.sum([component['area']*component['structure'].calculate_u_value()*deltaT*hours for component in self.components])/1000.0


    def calc_annual_transmission_heat_loss_timeseries(self, climatedata: pd.DataFrame, Tinner = 20.0, T_heating=17.0) -> float:
        """
        
        T_heating: Bis zu dieser Temperatur wird geheizt.
        
        """

        transmission_heat_loss = {}

        airtemp = climatedata['Tair'].copy()
        airtemp[airtemp>T_heating] = np.NaN

        for component in self.components:

            U_component = component['structure'].calculate_u_value()
            A_component = component['area']

            transmission_heat_loss[component['name']] = (Tinner - airtemp).mul(U_component).mul(A_component)

        self.transmission_heat_loss_ts = pd.concat(transmission_heat_loss).unstack(level=0)


    def info(self):
        
        data = [{'name': component['name'], 'Area': component['area'], 'U-Value': component['structure'].calculate_u_value()} for component in self.components]
        df = pd.DataFrame(data)
        
        df = df.set_index('name')
        return df