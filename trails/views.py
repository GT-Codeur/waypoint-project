# trails/views.py
from django.shortcuts import render
from .models import Trail

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
    # Fetch only open trails ordered by distance
    open_trails = Trail.objects.filter(is_open=True).order_by('distance_km')

    context = {
        "trails": open_trails,
    }
    return render(request, "catalog.html", context)
