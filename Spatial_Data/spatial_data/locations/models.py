from django.db import models
from django.db.models import JSONField

class Continent(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=255)
    iso_code = models.CharField(max_length=10, unique=True)
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE)
    polygon = JSONField(null=True, blank=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=255)
    region_code = models.CharField(max_length=10)
    country = models.ForeignKey(Country,  on_delete=models.CASCADE)
    polygon = JSONField(null=True, blank=True) 


    class Meta:
        unique_together = ("region_code","country") 

    def __str__(self):
        return self.name

    def get_polygon_boundary(self):
        return self.polygon

    def get_center_location(self):
        # GeoJSON format: {"type": "Polygon", "coordinates": [[[x1, y1], [x2, y2], ..., [xn, yn]]]}
        coordinates = self.polygon.get('coordinates', [])
        
        if not coordinates:
            return None

        # Flatten the list of coordinates (assuming the polygon has one outer ring)
        flat_coords = [coord for ring in coordinates for coord in ring]

        # Calculate the centroid by averaging the coordinates
        num_coords = len(flat_coords)
        if num_coords == 0:
            return None

        # Sum the X and Y values of the coordinates
        x_sum = sum(coord[0] for coord in flat_coords)
        y_sum = sum(coord[1] for coord in flat_coords)

        # Compute the average of the coordinates to get the centroid
        centroid_x = x_sum / num_coords
        centroid_y = y_sum / num_coords

        return (centroid_x, centroid_y)



class City(models.Model):
    name = models.CharField(max_length=255)
    city_code = models.CharField(max_length=10)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    polygon = JSONField(null=True, blank=True) 


    class Meta:
        unique_together = ("city_code","region")

    def __str__(self):
        return self.name

    def get_center_location(self):
        if not self.polygon:
            return None
        
        # GeoJSON format: {"type": "Polygon", "coordinates": [[[x1, y1], [x2, y2], ..., [xn, yn]]]}
        coordinates = self.polygon.get('coordinates', [])
        
        if not coordinates:
            return None

        # Flatten the list of coordinates (assuming the polygon has one outer ring)
        flat_coords = [coord for ring in coordinates for coord in ring]

        # Calculate the centroid by averaging the coordinates
        num_coords = len(flat_coords)
        if num_coords == 0:
            return None

        # Sum the X and Y values of the coordinates
        x_sum = sum(coord[0] for coord in flat_coords)
        y_sum = sum(coord[1] for coord in flat_coords)

        # Compute the average of the coordinates to get the centroid
        centroid_x = x_sum / num_coords
        centroid_y = y_sum / num_coords

        return (centroid_x, centroid_y)


class Address(models.Model):
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    city = models.ForeignKey(City, on_delete=models.CASCADE)


    class Meta:
        unique_together = ("latitude", "longitude","address")

    def __str__(self):
        return self.address