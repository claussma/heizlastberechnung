import polars as pl
_ = pl.Config.set_tbl_hide_dataframe_shape(True)
from wetterdienst import Settings
from wetterdienst.provider.dwd.observation import DwdObservationRequest, DwdObservationDataset, DwdObservationPeriod, DwdObservationResolution
import datetime as dt
from wetterdienst.metadata.parameter import Parameter

class WeatherData():
    def __init__(self, station_id: int = 1048, nyears=2) -> None:

        self.station_id = station_id

        year = dt.datetime.now().year - 1

        self.start_date = dt.datetime(year-nyears, 6, 1)
        self.end_date = dt.datetime(year, 5, 31)

    def _rename_columns(self):

        self.data.rename(columns={'temperature_air': 'Tair'}, inplace=True)
        self.data.rename(columns={'solar': 'radiation'}, inplace=True)



    def _convert_units(self):

        # Kelvin to °C
        self.data['Tair'] = self.data['Tair'] - 273.15
        
        # to kWh/m^2
        self.data['radiation'] = self.data['radiation'].mul(2.778).div(100*100).div(1000) # J/cm^2 in Wh/m^2 mit 1 W=1 J/s


    def load_data(self):

        settings = Settings( # default
            ts_shape="long",  # tidy data
            ts_humanize=True,  # humanized parameters
            ts_si_units=True  # convert values to SI units
        )
        request = DwdObservationRequest(
            parameter=['temperature_air_mean_200', 'radiation_global'],
            resolution=DwdObservationResolution.HOURLY,
            start_date=self.start_date,
            end_date=self.end_date, 
            settings=settings
            ).filter_by_station_id(station_id=(self.station_id))
        self.station = request.df

        self.data = request.values.all().df.to_pandas()
        self.data = self.data.pivot_table(values='value', columns='dataset', index='date')

        # rename parameters
        self._rename_columns()

        # convert units
        self._convert_units()