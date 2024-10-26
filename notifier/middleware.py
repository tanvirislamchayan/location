from ipware import get_client_ip
from .utils import send_telegram_message
from django.utils.deprecation import MiddlewareMixin
import geoip2.database
from django.conf import settings

class VisitorNotificationMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the 'session_visit' cookie is set
        session_visit = request.COOKIES.get('session_visit')

        if not session_visit:
            # Get the client IP
            ip, _ = get_client_ip(request)
            print(f'ip {ip}')

            if ip:
                # Determine the visitor's country
                country = self.get_country_from_ip(ip)

                # Send a notification to Telegram
                message = f"New visitor from {country} (IP: {ip}) visited the site. Developed By Tanvir Islam"
                send_telegram_message(message)

            # Continue processing the request
            response = self.get_response(request)

            # Set the 'session_visit' cookie to mark the session
            response.set_cookie('session_visit', 'true')
            return response
        else:
            # Continue processing the request if cookie is already set
            return self.get_response(request)

    def get_country_from_ip(self, ip='108.162.226.10'):
        print(f'get_country_from_ip')
        try:
            reader = geoip2.database.Reader(f"{settings.GEOIP_PATH}/GeoLite2-Country.mmdb")
            print(f'reader {reader}')
            response = reader.country(ip)
            print(f'response {response}')
            country = response.country.name
            print(f'country {country}')
            reader.close()
            return country
        except geoip2.errors.AddressNotFoundError:
            return "Unknown Country"
