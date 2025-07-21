# -*- coding: utf-8 -*-

import base64
from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions

from odoo.http import request
import requests
from lxml import etree
from odoo import models,fields
from meteostat import Point, Hourly, Daily
import logging

_logger = logging.getLogger(__name__)
THUNDERSTORM_WEATHER_CODES = [95, 96, 97, 98, 99]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ks_name = fields.Char()

    def action_download_x86_file(self):
        self.ensure_one()
        now = datetime.now()

        # Render QWeb template
        values = {
            'order': self,
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
        }
        xml_body = request.env['ir.ui.view']._render_template(
            'ks_gaeb.x86_sale_order_template', values
        )

        # Prepend the XML declaration manually
        full_xml = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_body}'

        # Create attachment for download
        filename = f"{self.name}.x86"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(full_xml.encode('utf-8')),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/octet-stream',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_download_d86_file(self):
        self.ensure_one()

        currency = self.currency_id.name if self.currency_id else 'EUR'

        rendered_text = request.env['ir.ui.view']._render_template(
            'ks_gaeb.gaeb_d86_sale_template',
            {
                'order': self,
                'currency': currency,
            }
        )

        # Rendered text is a list of strings joined by newlines
        content = rendered_text.strip()

        filename = f"{self.name}.d86"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(content.encode('utf-8')),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'text/plain',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    # def action_download_d86_file(self):
    #     # Define location (Berlin)
    #     berlin = Point(52.5244, 13.4105)
    #
    #     # Today's date
    #     now = datetime.now()
    #     start = datetime(now.year, now.month, now.day)
    #     end = now  # Up to current hour
    #
    #     # Fetch hourly data
    #     data = Hourly(berlin, start, end)
    #     data = data.fetch()
    #
    #     if not data.empty:
    #         last = data.iloc[-1]  # Most recent hour's data
    #         temp = last['temp']  # °C
    #         prcp = last['prcp']  # mm
    #         snow = last['snow']  # cm
    #         wspd = last['wspd']  # km/h
    #
    #         # Determine weather condition
    #         if snow and snow > 0:
    #             condition = "❄️ Snowfall"
    #         elif prcp and prcp > 0:
    #             if wspd and wspd > 30:
    #                 condition = "⛈️ Thunderstorm likely"
    #             else:
    #                 condition = "🌧️ Rain"
    #         else:
    #             condition = "☀️ Clear / No Rain"
    #
    #         print(f"Current Berlin Weather ({last.name.strftime('%Y-%m-%d %H:%M')}):")
    #         print(f"Temperature: {temp}°C")
    #         print(f"Precipitation: {prcp} mm")
    #         print(f"Condition: {condition}")
    #     else:
    #         print("❌ No hourly data available for today.")

    # @api.model
    # def action_download_d86_file(self, location_name=None, latitude=52.5244, longitude=13.4105, start_date_str='2025-06-01', end_date_str='2025-06-05',
    #                                  elevation=None):
    #     """
    #     Fetches daily weather data for a given location and specific date range.
    #     Creates/updates weather.data records for each day in the range.
    #
    #     :param location_name: Name of the location (e.g., 'Berlin').
    #     :param latitude: Latitude of the location.
    #     :param longitude: Longitude of the location.
    #     :param start_date_str: Start date in 'YYYY-MM-DD' format.
    #     :param end_date_str: End date in 'YYYY-MM-DD' format.
    #     :param elevation: Optional elevation in meters.
    #     :return: True if data was fetched successfully, False otherwise.
    #     """
    #     try:
    #         start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #         end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    #     except ValueError:
    #         _logger.error("Invalid date format. Please use 'YYYY-MM-DD'.")
    #         return False
    #
    #     if start_date > end_date:
    #         _logger.error("Start date cannot be after end date.")
    #         return False
    #
    #     _logger.info(f"Attempting to fetch weather data for {location_name} from {start_date_str} to {end_date_str}")
    #
    #     try:
    #         # Create Point for the location
    #         location = Point(latitude, longitude, elevation)
    #
    #         # Get daily data for the specified range
    #         data = Daily(location, start_date, end_date)
    #         data = data.fetch()
    #
    #         if data is not None and not data.empty:
    #             for index, row in data.iterrows():
    #                 current_date = index.date()
    #                 # Check if a record for this location and date already exists
    #                 # existing_record = self.search([
    #                 #     ('name', '=', location_name),
    #                 #     ('date', '=', current_date)
    #                 # ], limit=1)
    #
    #                 vals = {
    #                     'name': location_name,
    #                     'latitude': latitude,
    #                     'longitude': longitude,
    #                     'elevation': elevation,
    #                     'date': current_date,
    #                     'temperature_avg': row.tavg,
    #                     'temperature_min': row.tmin,
    #                     'temperature_max': row.tmax,
    #                     'precipitation': row.prcp,
    #                     'snow_depth': row.snow,
    #                     'wind_speed': row.wspd,
    #                     'pressure': row.pres,
    #                     'snow': row.snow,
    #                     'wind_dir': row.wdir,
    #                     'wind_pgt': row.wpgt,
    #                     'tsun': row.tsun,
    #                     'precipitation': row.prcp,
    #                 }
    #
    #                 # if existing_record:
    #                 #     existing_record.write(vals)
    #                 #     _logger.info(f"Updated weather data for {location_name} on {current_date}")
    #                 # else:
    #                 #     self.create(vals)
    #                 #     _logger.info(f"Created weather data for {location_name} on {current_date}")
    #             return True
    #         else:
    #             _logger.warning(
    #                 f"No weather data found for {location_name} between {start_date_str} and {end_date_str}.")
    #             return False
    #
    #     except Exception as e:
    #         _logger.error(
    #             f"Error fetching weather data for {location_name} in range {start_date_str} to {end_date_str}: {e}")
    #         return False

    # @api.model
    # def action_download_d86_file(self, location_name=None, latitude=52.5244, longitude=13.4105,
    #                              start_date_str='2025-06-01', end_date_str='2025-06-05', elevation=None):
    #     """
    #     Fetches historical hourly weather data from Bright Sky API for a given location and date range.
    #     Aggregates hourly data to daily and creates/updates weather.data records.
    #
    #     Note: Bright Sky provides hourly data. We'll aggregate to daily.
    #     """
    #     BRIGHTSKY_BASE_URL = "https://api.brightsky.dev/weather"
    #
    #     try:
    #         start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d')
    #         end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d')
    #     except ValueError:
    #         _logger.error("Bright Sky: Invalid date format. Please use 'YYYY-MM-DD'.")
    #         return False
    #
    #     if start_date_obj > end_date_obj:
    #         _logger.error("Bright Sky: Start date cannot be after end date.")
    #         return False
    #
    #     _logger.info(
    #         f"Bright Sky: Attempting to fetch weather data for {location_name} from {start_date_str} to {end_date_str}")
    #
    #     all_days_data = {}  # To store aggregated daily data
    #
    #     current_date_iterator = start_date_obj
    #     while current_date_iterator <= end_date_obj:
    #         query_date_str = current_date_iterator.strftime('%Y-%m-%d')
    #         params = {
    #             'lat': latitude,
    #             'lon': longitude,
    #             'date': query_date_str,
    #             'tz': 'UTC'  # Using UTC for consistency, adjust if local timezone is preferred
    #         }
    #
    #         try:
    #             response = requests.get(BRIGHTSKY_BASE_URL, params=params, timeout=10)  # Added timeout
    #             response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
    #             data = response.json()
    #
    #             if 'weather' in data and data['weather']:
    #                 hourly_data = data['weather']
    #
    #                 # Initialize daily aggregates
    #                 daily_temp_sum = 0
    #                 daily_temp_count = 0
    #                 daily_temp_min = float('inf')
    #                 daily_temp_max = float('-inf')
    #                 daily_precipitation = 0
    #                 daily_sunshine = 0
    #                 daily_wind_speed_sum = 0
    #                 daily_wind_speed_count = 0
    #                 daily_pressure_sum = 0
    #                 daily_pressure_count = 0
    #                 daily_humidity_sum = 0
    #                 daily_humidity_count = 0
    #
    #                 daily_weather_codes = set()  # To find the "most severe" or common code
    #                 brightsky_source = data.get('sources', [{}])[0].get('id', 'N/A')  # Get source from first source
    #
    #                 for hour_record in hourly_data:
    #                     # Temperatures
    #                     if hour_record.get('temperature') is not None:
    #                         temp = hour_record['temperature']
    #                         daily_temp_sum += temp
    #                         daily_temp_count += 1
    #                         daily_temp_min = min(daily_temp_min, temp)
    #                         daily_temp_max = max(daily_temp_max, temp)
    #
    #                     # Precipitation
    #                     if hour_record.get('precipitation') is not None:
    #                         daily_precipitation += hour_record['precipitation']
    #
    #                     # Sunshine
    #                     if hour_record.get('sunshine') is not None:
    #                         daily_sunshine += hour_record['sunshine']
    #
    #                     # Wind Speed (assuming 'wind_speed' is km/h, check Bright Sky docs)
    #                     if hour_record.get('wind_speed') is not None:
    #                         wind_speed = hour_record['wind_speed']
    #                         daily_wind_speed_sum += wind_speed
    #                         daily_wind_speed_count += 1
    #
    #                     # Pressure
    #                     if hour_record.get('pressure_msl') is not None:  # Mean sea level pressure
    #                         pressure = hour_record['pressure_msl']
    #                         daily_pressure_sum += pressure
    #                         daily_pressure_count += 1
    #
    #                     # Humidity
    #                     if hour_record.get('relative_humidity') is not None:
    #                         humidity = hour_record['relative_humidity']
    #                         daily_humidity_sum += humidity
    #                         daily_humidity_count += 1
    #
    #                     # Weather Code - collect all unique codes for the day
    #                     if hour_record.get('weather_code') is not None:
    #                         daily_weather_codes.add(hour_record['weather_code'])
    #
    #                 # Determine daily aggregated values
    #                 tavg = daily_temp_sum / daily_temp_count if daily_temp_count > 0 else None
    #                 wspd = daily_wind_speed_sum / daily_wind_speed_count if daily_wind_speed_count > 0 else None
    #                 pres = daily_pressure_sum / daily_pressure_count if daily_pressure_count > 0 else None
    #                 rhum = daily_humidity_sum / daily_humidity_count if daily_humidity_count > 0 else None
    #
    #                 # For weather code, you might choose:
    #                 # 1. The highest (most severe) code
    #                 # 2. Any code indicating a thunderstorm
    #                 # For simplicity, let's just pick the max code observed in the day
    #                 # Or, better, check if ANY thunderstorm code is present.
    #                 daily_weather_code_val = max(daily_weather_codes) if daily_weather_codes else None
    #                 has_thunderstorm_val = False
    #                 if daily_weather_code_val:
    #                     # Check if any observed code is a thunderstorm code
    #                     if any(code in THUNDERSTORM_WEATHER_CODES for code in daily_weather_codes):
    #                         has_thunderstorm_val = True
    #
    #                 all_days_data[current_date_iterator.date()] = {
    #                     'name': location_name,
    #                     'latitude': latitude,
    #                     'longitude': longitude,
    #                     'date': current_date_iterator.date(),
    #                     'temperature_avg': tavg,
    #                     'temperature_min': daily_temp_min if daily_temp_min != float('inf') else None,
    #                     'temperature_max': daily_temp_max if daily_temp_max != float('-inf') else None,
    #                     'precipitation': daily_precipitation,
    #                     'sunshine': daily_sunshine,
    #                     'wind_speed': wspd,
    #                     'pressure': pres,
    #                     'humidity': rhum,
    #                     'weather_code': daily_weather_code_val,
    #                     'has_thunderstorm': has_thunderstorm_val,
    #                     'brightsky_source': brightsky_source,
    #                 }
    #             else:
    #                 _logger.warning(
    #                     f"Bright Sky: No hourly weather data found for {location_name} on {query_date_str}.")
    #
    #         except requests.exceptions.RequestException as e:
    #             _logger.error(f"Bright Sky: Network or API error for {location_name} on {query_date_str}: {e}")
    #             # Continue to next day, or break if essential data
    #         except Exception as e:
    #             _logger.error(f"Bright Sky: Unexpected error for {location_name} on {query_date_str}: {e}")
    #
    #         current_date_iterator += timedelta(days=1)  # Move to the next day
    #
    #     # Now, process the aggregated daily data
    #     if all_days_data:
    #         for daily_date, vals in all_days_data.items():
    #             # existing_record = self.search([
    #             #     ('name', '=', location_name),
    #             #     ('date', '=', daily_date)
    #             # ], limit=1)
    #             print(daily_date,'-------------------------------------',vals)
    #
    #             # Ensure elevation and snow_depth are handled if Bright Sky doesn't provide them
    #             # Bright Sky often doesn't have a direct 'snow_depth' field for daily summary
    #             # You might need to add logic to calculate/infer this if critical.
    #             # For now, we'll just set them to None if not explicitly from Bright Sky or leave as is.
    #             # vals['elevation'] = None  # Bright Sky doesn't typically return station elevation in 'weather' data
    #             #
    #             # if existing_record:
    #             #     existing_record.write(vals)
    #             #     _logger.info(f"Bright Sky: Updated weather data for {location_name} on {daily_date}")
    #             # else:
    #             #     self.create(vals)
    #             #     _logger.info(f"Bright Sky: Created weather data for {location_name} on {daily_date}")
    #         return True
    #     else:
    #         _logger.warning(
    #             f"Bright Sky: No data aggregated for {location_name} between {start_date_str} and {end_date_str}.")
    #         return False

    # You can keep get_hourly_weather_for_location if you need hourly data as well
    # from meteostat, or you can adjust it to use Bright Sky for hourly.
    # @api.model
    # def get_hourly_weather_for_location(self, latitude, longitude, elevation=None, start_datetime=None, end_datetime=None):
    #     pass



