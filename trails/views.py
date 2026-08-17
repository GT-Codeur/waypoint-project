# trails/views.py
from django.shortcuts import render, get_object_or_404
from .models import Park, Trail

def home(request):
    context = {
        "greeting": "Welcome to Waypoint Trail Explorer!"
    }
    return render(request, "home.html", context)


def report(request):
    if request.method == "POST":
        reporter_name = request.POST.get("name", "Hiker").strip()
        email = request.POST.get("email", "").strip()
        trail_name = request.POST.get("trail", "Unknown Trail").strip()
        note = request.POST.get("note", "").strip()

        context = {
            "reporter_name": reporter_name or "Hiker",
            "email": email,
            "trail_name": trail_name,
            "note": note,
        }
        return render(request, "report_thanks.html", context)

    return render(request, "report.html")


def search(request):
    query = request.GET.get("q", "").strip()
    context = {
        "query": query,
    }
    return render(request, "search.html", context)


def catalog(request):
    # Base query fetching open trails with efficient FK join
    open_trails = Trail.objects.filter(is_open=True).select_related('park')

    # WP-705: Cross-relation filter parameter (?park=)
    selected_park_id = request.GET.get('park', '').strip()
    if selected_park_id.isdigit():
        open_trails = open_trails.filter(park_id=int(selected_park_id))

    # Fetch all parks for dropdown filter UI
    all_parks = Park.objects.all()

    context = {
        "trails": open_trails,
        "parks": all_parks,
        "selected_park_id": selected_park_id,
    }
    return render(request, "catalog.html", context)


def trail_detail(request, pk):
    trail = get_object_or_404(Trail.objects.select_related('park'), pk=pk)

    # Cross-relation query: Get other trails in the exact same park
    sibling_trails = []
    if trail.park:
        sibling_trails = trail.park.trails.filter(is_open=True).exclude(pk=trail.pk)[:3]

    context = {
        "trail": trail,
        "sibling_trails": sibling_trails,
    }
    return render(request, "trail_detail.html", context)
