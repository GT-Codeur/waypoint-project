from django.contrib import admin
from .models import Park, Trail


class TrailInline(admin.TabularInline):
    model = Trail
    extra = 1
    fields = ('name', 'distance_km', 'elevation_gain', 'difficulty', 'is_open')


@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'trail_count', 'added')
    search_fields = ('name', 'region')
    inlines = [TrailInline]

    def trail_count(self, obj):
        return obj.trails.count()
    trail_count.short_description = 'Total Trails'


@admin.register(Trail)
class TrailAdmin(admin.ModelAdmin):
    list_display = ('name', 'park', 'distance_km', 'elevation_gain', 'difficulty', 'is_open')
    list_filter = ('park', 'is_open', 'difficulty')
    search_fields = ('name', 'park__name')
    list_editable = ('is_open',)
