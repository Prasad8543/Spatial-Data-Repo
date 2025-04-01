"""
URL configuration for spatial_data project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from locations.views import ContinentViewSet, CountryViewSet, LocationListCreateAPIView, RegionViewSet, CityViewSet, AddressViewSet

router = DefaultRouter()
router.register("api/v1/continents", ContinentViewSet)
router.register("api/v1/countries", CountryViewSet)
router.register("api/v1/regions", RegionViewSet)
router.register("api/v1/cities", CityViewSet)
router.register("api/v1/addresses", AddressViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/locations/",LocationListCreateAPIView.as_view(),name="locations_list_create"),
    path('', include(router.urls))
]
