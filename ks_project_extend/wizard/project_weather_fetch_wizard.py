# -*- coding: utf-8 -*-
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
from odoo import models, fields, api, _

from meteostat import Hourly, Daily, Stations, units
import pandas as pd

from datetime import datetime

# Mapping of weather condition codes
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    4: "Fog",
    5: "Depositing rime fog",
    6: "Light drizzle",
    7: "Drizzle",
    8: "Dense drizzle",
    9: "Light freezing drizzle",
    10: "Freezing drizzle",
    11: "Dense freezing drizzle",
    12: "Slight rain",
    13: "Rain",
    14: "Heavy rain",
    15: "Light freezing rain",
    16: "Freezing rain",
    17: "Heavy freezing rain",
    18: "Slight snow fall",
    19: "Snow fall",
    20: "Heavy snow fall",
    21: "Snow grains",
    22: "Slight rain showers",
    23: "Rain showers",
    24: "Violent rain showers",
    25: "Slight snow showers",
    26: "Snow showers",
    27: "Heavy snow showers",
    28: "Thunderstorm",
    29: "Thunderstorm with hail",
}


class ProjectWeatherFetchWizard(models.TransientModel):
    _name = 'project.weather.fetch.wizard'
    _description = 'Fetch Weather Wizard'

    project_id = fields.Many2one('project.project', string="Task", required=True, readonly=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    latitude = fields.Char(string="Latitude", required=True)
    longitude = fields.Char(string="Longitude", required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        project = self.env['project.project'].browse(self.env.context.get('active_id'))
        if project.latitude is False or project.longitude is False:
            raise UserError("Project has no latitude/longitude. Please set coordinates first.")

        res.update({
            'project_id': project.id,
            'latitude': project.latitude,
            'longitude': project.longitude,
        })
        return res

    # def action_fetch_weather(self):
    #     self.ensure_one()
    #
    #     # Date range
    #     start = datetime.now() - timedelta(days=3)
    #     end = datetime.now()
    #
    #     # 2. Create a DwdObservationRequest with desired parameter
    #     request = DwdObservationRequest("temperature_air_mean_200","daily", start, end)
    #
    #     # 3. Filter stations by geographic proximity (within 50 km)
    #     stations = request.filter_by_distance(
    #         latlon=(self.latitude, self.longitude),
    #         distance=50,
    #         unit="km"
    #     ).all()
    #
    #     if stations.empty:
    #         print("❌ No station found.")
    #     else:
    #         station = stations.iloc[0]
    #         print("✅ Nearest Station:")
    #         print(f"ID      : {station['station_id']}")
    #         print(f"Name    : {station['station_name']}")
    #         print(f"Distance: {station['distance']:.2f} km")
    #
    #     # station_id = '01048'  # Berlin-Dahlem – available in both folders
    #     lines_to_create = []
    #
    #     def extract_lines(url):
    #         try:
    #             resp = requests.get(url, timeout=30)
    #             resp.raise_for_status()
    #             with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
    #                 prod = next((n for n in zf.namelist() if n.startswith('produkt_')), None)
    #                 if not prod:
    #                     raise UserError(_("No data file inside ZIP %s") % url)
    #                 return zf.read(prod).decode('latin-1').splitlines()[1:]  # skip header
    #         except Exception as e:
    #             raise UserError(_("Failed download/extract from %s:\n%s") % (url, e))
    #
    #     data_lines = []
    #
    #     # Historical (older than 500 days)
    #     if self.start_date < fields.Date.from_string('2021-01-01'):
    #         hist_zip = f"tageswerte_KL_{station_id}_19900101_20201231_hist.zip"
    #         hist_url = f"https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/{hist_zip}"
    #         data_lines += extract_lines(hist_url)
    #
    #     # Recent (last ~500 days rolling)
    #     if self.end_date >= fields.Date.from_string('2021-01-01'):
    #         recent_zip = f"tageswerte_KL_{station_id}_akt.zip"
    #         recent_url = f"https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/recent/{recent_zip}"
    #         data_lines += extract_lines(recent_url)
    #
    #     for line in data_lines:
    #         parts = [c.strip() for c in line.split(';')]
    #         try:
    #             rec_date = datetime.strptime(parts[1], '%Y%m%d').date()
    #             if self.start_date <= rec_date <= self.end_date:
    #                 lines_to_create.append((0, 0, {
    #                     'report_date': rec_date,
    #                     'temp_min': float(parts[5]) if parts[5] != '-999' else False,
    #                     'temp_max': float(parts[6]) if parts[6] != '-999' else False,
    #                     'humidity': float(parts[13]) if parts[13] != '-999' else False,
    #                     'conditions': f"Cloud Cover: {parts[15]}/8, Sunshine: {parts[14]}h"
    #                 }))
    #         except (ValueError, IndexError):
    #             continue
    #
    #     self.task_id.weather_ids = [(5, 0, 0)] + lines_to_create
    #
    #     if not lines_to_create:
    #         raise UserError(_("No weather data found in the selected date range."))

    # def action_fetch_weather(self):
    #     self.ensure_one()
    #     lines_to_create = []
    #
    #     # Get lat/lon from task or another source
    #     lat = self.latitude
    #     lon = self.longitude
    #
    #     # Step 1: Get nearest station using wetterdienst
    #     try:
    #         request = DwdObservationRequest(
    #             parameter="temperature_air_mean_200",  # dummy param to query station
    #             resolution=DwdObservationResolution.DAILY,
    #             period=DwdObservationPeriod.RECENT
    #         )
    #         stations = request.filter_by_latlon(latitude=lat, longitude=lon).all()
    #         if stations.empty:
    #             raise UserError(_("No nearby DWD weather station found."))
    #
    #         station_id = stations.iloc[0]["station_id"]
    #         station_name = stations.iloc[0]["station_name"]
    #     except Exception as e:
    #         raise UserError(_("Failed to find nearest weather station: %s") % str(e))
    #
    #     def extract_lines(url):
    #         try:
    #             resp = requests.get(url, timeout=30)
    #             resp.raise_for_status()
    #             with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
    #                 prod = next((n for n in zf.namelist() if n.startswith('produkt_')), None)
    #                 if not prod:
    #                     raise UserError(_("No data file inside ZIP %s") % url)
    #                 return zf.read(prod).decode('latin-1').splitlines()[1:]  # skip header
    #         except Exception as e:
    #             raise UserError(_("Failed to download or extract weather data:\n%s") % str(e))
    #
    #     data_lines = []
    #
    #     # Historical (before 2021)
    #     if self.start_date < fields.Date.from_string('2021-01-01'):
    #         hist_zip = f"tageswerte_KL_{station_id}_19900101_20201231_hist.zip"
    #         hist_url = f"https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/{hist_zip}"
    #         data_lines += extract_lines(hist_url)
    #
    #     # Recent (2021+)
    #     if self.end_date >= fields.Date.from_string('2021-01-01'):
    #         recent_zip = f"tageswerte_KL_{station_id}_akt.zip"
    #         recent_url = f"https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/recent/{recent_zip}"
    #         data_lines += extract_lines(recent_url)
    #
    #     for line in data_lines:
    #         parts = [c.strip() for c in line.split(';')]
    #         try:
    #             rec_date = datetime.strptime(parts[1], '%Y%m%d').date()
    #             if self.start_date <= rec_date <= self.end_date:
    #                 lines_to_create.append((0, 0, {
    #                     'report_date': rec_date,
    #                     'temp_min': float(parts[5]) if parts[5] != '-999' else False,
    #                     'temp_max': float(parts[6]) if parts[6] != '-999' else False,
    #                     'humidity': float(parts[13]) if parts[13] != '-999' else False,
    #                     'conditions': f"Cloud Cover: {parts[15]}/8, Sunshine: {parts[14]}h"
    #                 }))
    #         except (ValueError, IndexError):
    #             continue
    #
    #     self.task_id.weather_ids = [(5, 0, 0)] + lines_to_create
    #
    #     if not lines_to_create:
    #         raise UserError(_("No weather data found in the selected date range."))

    # def action_fetch_weather(self):
    #     self.ensure_one()
    #     # 💥 Debug and ensure float conversion
    #     try:
    #         lat_raw = self.latitude
    #         lon_raw = self.longitude
    #         _logger.info("Latitude raw: %s | Longitude raw: %s", lat_raw, lon_raw)
    #
    #         lat = float(lat_raw)
    #         lon = float(lon_raw)
    #     except Exception as e:
    #         raise UserError(_("Latitude or Longitude are invalid or missing. Error: %s") % str(e))
    #
    #     if not (-90 <= lat <= 90 and -180 <= lon <= 180):
    #         raise UserError(_("Latitude must be between -90 and 90, Longitude between -180 and 180."))
    #
    #     # ✅ This is now safe
    #
    #     # Convert Odoo dates to datetime
    #     try:
    #         start_dt = datetime.combine(self.start_date, datetime.min.time())
    #         end_dt = datetime.combine(self.end_date, datetime.max.time())
    #     except Exception as e:
    #         raise UserError(_("Invalid date range: %s") % str(e))
    #
    #     # Step 1: Find nearest station via Meteostat
    #     try:
    #         stations = Stations()
    #         nearest = stations.nearby(lat, lon).fetch(1)
    #         if nearest.empty:
    #             raise UserError(_("No weather station found near the given coordinates."))
    #         station_id = nearest.index[0]
    #     except Exception as e:
    #         raise UserError(_("Failed to find weather station: %s") % str(e))
    #
    #     # Step 2: Fetch daily weather data
    #     try:
    #         data = Daily(station_id, start=start_dt, end=end_dt)
    #         data = data.convert(units.imperial)  # Optional: convert to imperial or metric
    #         df = data.fetch()
    #     except Exception as e:
    #         raise UserError(_("Failed to fetch weather data: %s") % str(e))
    #
    #     if df.empty:
    #         raise UserError(_("No weather data available for selected dates."))
    #
    #     # Step 3: Map & create records
    #     lines_to_create = []
    #     for date, row in df.iterrows():
    #         lines_to_create.append((0, 0, {
    #             'report_date': date.date(),
    #             'temp_min': row['tmin'] if not pd.isna(row['tmin']) else False,
    #             'temp_max': row['tmax'] if not pd.isna(row['tmax']) else False,
    #             'humidity': row['rhum'] if 'rhum' in row and not pd.isna(row['rhum']) else False,
    #             'conditions': f"Precip: {row['prcp']}mm, Wind: {row['wspd']}km/h" if 'prcp' in row else "",
    #         }))
    #
    #     # Step 4: Save to task
    #     self.task_id.weather_ids = [(5, 0, 0)] + lines_to_create
    #
    #     if not lines_to_create:
    #         raise UserError(_("Weather data was fetched, but no valid rows were found."))

    # def action_fetch_weather(self):
    #     self.ensure_one()
    #
    #     # Step 0: Validate and convert coordinates
    #     try:
    #         lat = float(self.latitude)
    #         lon = float(self.longitude)
    #     except Exception as e:
    #         raise UserError(_("Latitude or Longitude are invalid or missing. Error: %s") % str(e))
    #
    #     if not (-90 <= lat <= 90 and -180 <= lon <= 180):
    #         raise UserError(_("Latitude must be between -90 and 90, Longitude between -180 and 180."))
    #
    #     # Step 1: Validate and parse date range
    #     try:
    #         start_dt = datetime.combine(self.start_date, datetime.min.time())
    #         end_dt = datetime.combine(self.end_date, datetime.max.time())
    #     except Exception as e:
    #         raise UserError(_("Invalid date range: %s") % str(e))
    #
    #     # Step 2: Get nearest weather station
    #     try:
    #         stations = Stations()
    #         nearest = stations.nearby(lat, lon).fetch(1)
    #         if nearest.empty:
    #             raise UserError(_("No weather station found near the given coordinates."))
    #         station_id = nearest.index[0]
    #     except Exception as e:
    #         raise UserError(_("Failed to find weather station: %s") % str(e))
    #
    #     # Step 3: Fetch weather data
    #     try:
    #         weather = Daily(station_id, start_dt, end_dt)
    #         df = weather.fetch()
    #     except Exception as e:
    #         raise UserError(_("Failed to fetch weather data: %s") % str(e))
    #
    #     if df.empty:
    #         raise UserError(_("No weather data available for selected dates."))
    #
    #     # Step 4: Map and store data
    #     lines_to_create = []
    #     for date, row in df.iterrows():
    #         lines_to_create.append((0, 0, {
    #             'report_date': date.date(),
    #             'temp_min': row.get('tmin') if pd.notna(row.get('tmin')) else False,
    #             'temp_max': row.get('tmax') if pd.notna(row.get('tmax')) else False,
    #             'humidity': row.get('rhum') if pd.notna(row.get('rhum')) else False,
    #             'conditions': f"Precip: {row.get('prcp', 0)}mm, Wind: {row.get('wspd', 0)}km/h",
    #         }))
    #
    #     self.task_id.weather_ids = [(5, 0, 0)] + lines_to_create
    #
    #     if not lines_to_create:
    #         raise UserError(_("Weather data was fetched, but no valid rows were found."))

    # def action_fetch_weather(self):
    #     self.ensure_one()
    #
    #     # Step 1: Parse and validate coordinates
    #     try:
    #         lat = float(self.latitude)
    #         lon = float(self.longitude)
    #     except Exception as e:
    #         raise UserError(_("Latitude or Longitude are invalid or missing. Error: %s") % str(e))
    #
    #     if not (-90 <= lat <= 90 and -180 <= lon <= 180):
    #         raise UserError(_("Latitude must be between -90 and 90, Longitude between -180 and 180."))
    #
    #     # Step 2: Convert Odoo dates to Python datetime
    #     try:
    #         start_dt = datetime.combine(self.start_date, datetime.min.time())
    #         end_dt = datetime.combine(self.end_date, datetime.max.time())
    #     except Exception as e:
    #         raise UserError(_("Invalid date range: %s") % str(e))
    #
    #     # Step 3: Find nearest weather station
    #     try:
    #         stations = Stations()
    #         nearest = stations.nearby(lat, lon).fetch(1)
    #         if nearest.empty:
    #             raise UserError(_("No weather station found near the given coordinates."))
    #         station_id = nearest.index[0]
    #     except Exception as e:
    #         raise UserError(_("Failed to find weather station: %s") % str(e))
    #
    #     # Step 4: Fetch daily weather data
    #     try:
    #         weather = Daily(station_id, start_dt, end_dt)
    #         df = weather.fetch()
    #     except Exception as e:
    #         raise UserError(_("Failed to fetch weather data: %s") % str(e))
    #
    #     if df.empty:
    #         raise UserError(_("No weather data available for selected dates."))
    #
    #     # Step 5: Map and create lines
    #     lines_to_create = []
    #
    #     for date, row in df.iterrows():
    #         # Intelligent fallback for behavior
    #         if pd.notna(row.get('coco')):
    #             coco_code = int(row['coco'])
    #             behavior = WEATHER_CODES.get(coco_code, "Unknown")
    #         else:
    #             if pd.notna(row.get('snow')) and float(row['snow']) > 0:
    #                 behavior = "Snowfall"
    #             elif pd.notna(row.get('prcp')) and float(row['prcp']) > 0:
    #                 behavior = "Rainfall"
    #             elif pd.notna(row.get('rhum')) and float(row['rhum']) > 90:
    #                 behavior = "Humid"
    #             else:
    #                 behavior = "Clear/Unknown"
    #
    #         snow = float(row['snow']) if pd.notna(row.get('snow')) else 0.0
    #         precip = float(row['prcp']) if pd.notna(row.get('prcp')) else 0.0
    #         wind = float(row['wspd']) if pd.notna(row.get('wspd')) else 0.0
    #
    #         lines_to_create.append((0, 0, {
    #             'report_date': date.date(),
    #             'temp_min': row['tmin'] if pd.notna(row.get('tmin')) else False,
    #             'temp_max': row['tmax'] if pd.notna(row.get('tmax')) else False,
    #             'humidity': row['rhum'] if pd.notna(row.get('rhum')) else False,
    #             'conditions': (
    #                 f"Behavior: {behavior}, "
    #                 f"Snow: {snow} cm, "
    #                 f"Precip: {precip} mm, "
    #                 f"Wind: {wind} km/h"
    #             ),
    #         }))
    #
    #     # Step 6: Replace existing lines on task
    #     self.task_id.weather_ids = [(5, 0, 0)] + lines_to_create
    #
    #     if not lines_to_create:
    #         raise UserError(_("Weather data was fetched, but no valid rows were found."))

    # def action_fetch_weather(self):
    #     self.ensure_one()
    #
    #     # Step 1: Parse and validate coordinates
    #     try:
    #         lat = float(self.latitude)
    #         lon = float(self.longitude)
    #     except Exception as e:
    #         raise UserError(_("Latitude or Longitude are invalid or missing. Error: %s") % str(e))
    #
    #     if not (-90 <= lat <= 90 and -180 <= lon <= 180):
    #         raise UserError(_("Latitude must be between -90 and 90, Longitude between -180 and 180."))
    #
    #     # Step 2: Convert Odoo dates to Python datetime
    #     try:
    #         start_dt = datetime.combine(self.start_date, datetime.min.time())
    #         end_dt = datetime.combine(self.end_date, datetime.max.time())
    #     except Exception as e:
    #         raise UserError(_("Invalid date range: %s") % str(e))
    #
    #     # Step 3: Find nearest weather station
    #     try:
    #         stations = Stations()
    #         nearest = stations.nearby(lat, lon).fetch(1)
    #         if nearest.empty:
    #             raise UserError(_("No weather station found near the given coordinates."))
    #         station_id = nearest.index[0]
    #     except Exception as e:
    #         raise UserError(_("Failed to find weather station: %s") % str(e))
    #
    #     # Step 4: Fetch daily weather data
    #     try:
    #         weather = Daily(station_id, start_dt, end_dt)
    #         df = weather.fetch()
    #     except Exception as e:
    #         raise UserError(_("Failed to fetch weather data: %s") % str(e))
    #
    #     if df.empty:
    #         raise UserError(_("No weather data available for selected dates."))
    #
    #     # Step 5: Map and create lines
    #     lines_to_create = []
    #
    #     for date, row in df.iterrows():
    #         # Step 5.1: Weather behavior logic
    #         coco_raw = row.get('coco')
    #         behavior = "Unknown"
    #
    #         if pd.notna(coco_raw):
    #             try:
    #                 coco_code = int(coco_raw)
    #                 behavior = WEATHER_CODES.get(coco_code, f"Unknown condition code: {coco_code}")
    #             except Exception:
    #                 behavior = f"Invalid condition code: {coco_raw}"
    #         else:
    #             # Inferred fallback if coco is missing
    #             if pd.notna(row.get('snow')) and float(row['snow']) > 0:
    #                 behavior = "Inferred: Snowfall"
    #             elif pd.notna(row.get('prcp')) and float(row['prcp']) > 0:
    #                 behavior = "Inferred: Rainfall"
    #             elif pd.notna(row.get('rhum')) and float(row['rhum']) > 90:
    #                 behavior = "Inferred: Very Humid"
    #             else:
    #                 behavior = "Inferred: Clear/Unknown"
    #
    #         # Step 5.2: Clean up other data safely
    #         snow = float(row['snow']) if pd.notna(row.get('snow')) else 0.0
    #         precip = float(row['prcp']) if pd.notna(row.get('prcp')) else 0.0
    #         wind = float(row['wspd']) if pd.notna(row.get('wspd')) else 0.0
    #
    #         lines_to_create.append((0, 0, {
    #             'report_date': date.date(),
    #             'temp_min': row['tmin'] if pd.notna(row.get('tmin')) else False,
    #             'temp_max': row['tmax'] if pd.notna(row.get('tmax')) else False,
    #             'humidity': row['rhum'] if pd.notna(row.get('rhum')) else False,
    #             'conditions': (
    #                 f"Behavior: {behavior}, "
    #                 f"Snow: {snow:.1f} cm, "
    #                 f"Precip: {precip:.1f} mm, "
    #                 f"Wind: {wind:.1f} km/h"
    #             ),
    #         }))
    #
    #     # Step 6: Replace existing lines
    #     self.task_id.weather_ids = [(5, 0, 0)] + lines_to_create
    #
    #     if not lines_to_create:
    #         raise UserError(_("Weather data was fetched, but no valid rows were found."))

    def action_fetch_weather(self):
        self.ensure_one()

        # Step 1: Parse and validate coordinates
        try:
            lat = float(self.latitude)
            lon = float(self.longitude)
        except Exception as e:
            raise UserError(_("Latitude or Longitude are invalid or missing. Error: %s") % str(e))

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise UserError(_("Latitude must be between -90 and 90, Longitude between -180 and 180."))

        # Step 2: Convert Odoo dates to Python datetime
        try:
            start_dt = datetime.combine(self.start_date, datetime.min.time())
            end_dt = datetime.combine(self.end_date, datetime.max.time())
        except Exception as e:
            raise UserError(_("Invalid date range: %s") % str(e))

        # Step 3: Find nearest weather station
        try:
            stations = Stations()
            nearest = stations.nearby(lat, lon).fetch(1)
            if nearest.empty:
                raise UserError(_("No weather station found near the given coordinates."))
            station_id = nearest.index[0]
        except Exception as e:
            raise UserError(_("Failed to find weather station: %s") % str(e))

        # Step 4: Fetch daily weather data
        try:
            weather = Daily(station_id, start_dt, end_dt)
            df = weather.fetch()
        except Exception as e:
            raise UserError(_("Failed to fetch weather data: %s") % str(e))

        if df.empty:
            raise UserError(_("No weather data available for selected dates."))

        # Step 5: Map and create lines
        lines_to_create = []

        for date, row in df.iterrows():
            # Safely extract values with fallback
            snow = float(row['snow']) if pd.notna(row.get('snow')) else 0.0
            precip = float(row['prcp']) if pd.notna(row.get('prcp')) else 0.0
            wind = float(row['wspd']) if pd.notna(row.get('wspd')) else 0.0

            # Step 5.1: Weather behavior logic
            coco_raw = row.get('coco')
            behavior = "Unknown"

            if pd.notna(coco_raw):
                try:
                    coco_code = int(coco_raw)
                    behavior = WEATHER_CODES.get(coco_code, f"Unknown condition code: {coco_code}")
                except Exception:
                    behavior = f"Invalid condition code: {coco_raw}"
            else:
                _logger.warning("Missing coco code for date %s (Station: %s)", date.date(), station_id)
                # Inferred fallback if coco is missing
                if snow > 0:
                    behavior = "Inferred: Snowfall"
                elif precip > 0:
                    behavior = "Inferred: Rainfall"
                elif pd.notna(row.get('rhum')) and float(row['rhum']) > 90:
                    behavior = "Inferred: Very Humid"
                elif wind > 15:
                    behavior = "Inferred: Windy"
                else:
                    behavior = "Inferred: Clear/Unknown"

            # Step 5.2: Append clean line
            lines_to_create.append((0, 0, {
                'report_date': date.date(),
                'temp_min': row['tmin'] if pd.notna(row.get('tmin')) else False,
                'temp_max': row['tmax'] if pd.notna(row.get('tmax')) else False,
                'humidity': row['rhum'] if pd.notna(row.get('rhum')) else False,
                'conditions': (
                    f"Behavior: {behavior}, "
                    f"Snow: {snow:.1f} cm, "
                    f"Precip: {precip:.1f} mm, "
                    f"Wind: {wind:.1f} km/h"
                ),
            }))

        # Step 6: Replace existing lines
        self.project_id.sudo().weather_ids = [(5, 0, 0)] + lines_to_create

        if not lines_to_create:
            raise UserError(_("Weather data was fetched, but no valid rows were found."))