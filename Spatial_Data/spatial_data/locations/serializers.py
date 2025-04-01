from rest_framework import serializers
from .models import Continent, Country, Region, City, Address

class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    continent = ContinentSerializer()

    class Meta:
        model = Country
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Region
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = City
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Address
        fields = '__all__'



class LocationRequestSerializer(serializers.Serializer):
    continent = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    region = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=255)


class LocationResponseSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    continent = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ["id", "address", "latitude", "longitude", "city", "region", "country","continent"]

    def get_city(self, obj):
        return {
            "id": obj.city.id,
            "name": obj.city.name,
            "city_code": obj.city.city_code,
            "polygon": obj.city.polygon,
            "region": obj.city.region.id
        } if obj.city else None

    def get_region(self, obj):
        return {
            "id": obj.city.region.id,
            "name": obj.city.region.name,
            "region_code": obj.city.region.region_code,
            "polygon": obj.city.region.polygon,
            "country": obj.city.region.country.id
        } if obj.city and obj.city.region else None

    def get_country(self, obj):
        return {
            "id": obj.city.region.country.id,
            "name": obj.city.region.country.name,
            "iso_code": obj.city.region.country.iso_code,
            "polygon": obj.city.region.country.polygon,
            "continent": obj.city.region.country.continent.id
        } if obj.city and obj.city.region and obj.city.region.country else None
    
    def get_continent(self,obj):
        return {
            "id": obj.city.region.country.continent.id,
            "name": obj.city.region.country.continent.name,
            "code": obj.city.region.country.continent.code,
        } if obj.city and obj.city.region and obj.city.region.country and obj.city.region.country.continent else None