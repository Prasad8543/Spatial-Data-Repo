from django.db import IntegrityError
from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers
from rest_framework.response import Response
from rest_framework import status
from geopy.geocoders import Nominatim
import requests
from rest_framework import viewsets

from .pagination import CursorSetPagination
from locations.serializers import ContinentSerializer, CountrySerializer, RegionSerializer, CitySerializer, AddressSerializer,LocationRequestSerializer, LocationResponseSerializer

from .models import Continent, Country, Region, City, Address


class LocationListCreateAPIView(generics.ListCreateAPIView):
    """
    API to list and create locations.
    """
    serializer_class = LocationResponseSerializer
    pagination_class = CursorSetPagination  # 🔹 Enable Cursor Pagination
    queryset = Address.objects.all().order_by("id")  # 🔹 Ensure ordering for pagination



    def get_osm_polygon(self, place_name):
        """
        Fetch polygon data from the Overpass API
        """
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        relation["name"="{place_name}"];
        out geom;
        """
        response = requests.get(overpass_url, params={"data": query})

        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])

            if elements:
                polygons = []
                for element in elements:
                    if "members" in element:
                        for member in element["members"]:
                            if member.get("type") == "way" and "geometry" in member:
                                coordinates = [[point["lon"], point["lat"]] for point in member["geometry"]]
                                polygons.append(coordinates)
                return {"type": "Polygon", "coordinates": polygons}

        return None


    def create(self, request, *args, **kwargs):
        """
        Handles the request to create a new address with city, region, country, and continent.
        """
        serializer = LocationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        breakpoint()

        continent_name = data.get("continent")
        country_name = data.get("country")
        region_name = data.get("region")
        city_name = data.get("city")
        address_text = data.get("address")

        # Initialize geolocator
        geolocator = Nominatim(user_agent="location_api")
        location = geolocator.geocode(f"{address_text}, {city_name}, {region_name}, {country_name}")

        if not location:
            return Response({"error": "Location not found"}, status=status.HTTP_400_BAD_REQUEST)

        latitude = location.latitude
        longitude = location.longitude

        # Get or create Continent
        continent, _ = Continent.objects.get_or_create(name=continent_name, code=continent_name[:2].upper())

        country = Country.objects.filter(name=country_name,iso_code=country_name[:2].upper()).first()
        if not country:
            country, _ = Country.objects.get_or_create(
                name=country_name,
                iso_code=country_name[:2].upper(),
                continent=continent,
                polygon = self.get_osm_polygon(country_name)
            )

        
        region = Region.objects.filter(name=region_name,region_code=region_name[:3].upper(),country=country).first()
        if not region:
            region, _ = Region.objects.get_or_create(
                name=region_name,
                region_code=region_name[:3].upper(),
                country=country,
                polygon = self.get_osm_polygon(region_name)
            )

        city = City.objects.filter(name=city_name,city_code=city_name[:3].upper(),region=region).first()
        if not city:
            city, _ = City.objects.get_or_create(
                name=city_name,
                city_code=city_name[:3].upper(),
                region=region,
                polygon = self.get_osm_polygon(city_name)
            )

        # Create Address
        try:
            address = Address.objects.create(
                address=address_text,
                latitude=latitude,
                longitude=longitude,
                city=city
            )
            
        except IntegrityError as e:
            # If a database constraint error occurs (e.g., unique violation)
            return Response(
                data={
                    "code":"already_exists",
                    "detail":"Address already exists"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = LocationResponseSerializer(address)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContinentViewSet(viewsets.ModelViewSet):
    queryset = Continent.objects.all()
    serializer_class = ContinentSerializer
    pagination_class = CursorSetPagination 


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = CursorSetPagination 


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    pagination_class = CursorSetPagination 


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = CursorSetPagination 


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    pagination_class = CursorSetPagination 