# trails/views.py
from django.shortcuts import render

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
    # Catalog dataset with at least 6 trail dicts
    trails_list = [
        {
            "name": "Cascade Pass Trail",
            "distance": 11.842,
            "elevation": 540,
            "difficulty": "Moderate",
            "is_open": True,
        },
        {
            "name": "Skyline Ridge Loop",
            "distance": 8.5,
            "elevation": 420,
            "difficulty": "Easy",
            "is_open": True,
        },
        {
            "name": "Mount Rainier Pinnacle",
            "distance": 14.375,
            "elevation": 1250,
            "difficulty": "Expert",
            "is_open": True,
        },
        {
            "name": "Wonderland Northern Arc",
            "distance": 32.110,
            "elevation": 2100,
            "difficulty": "Expert",
            "is_open": False,
        },
        {
            "name": "Emerald Ridge Walk",
            "distance": 5.2,
            "elevation": 180,
            "difficulty": "Easy",
            "is_open": True,
        },
        {
            "name": "Storm King Lookout",
            "distance": 6.891,
            "elevation": 630,
            "difficulty": "Hard",
            "is_open": False,
        },
    ]

    context = {
        "trails": trails_list,
    }
    return render(request, "catalog.html", context)