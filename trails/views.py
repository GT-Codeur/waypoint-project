# trails/views.py
from django.shortcuts import render

def home(request):
    context = {
        "greeting": "Welcome to Waypoint Trail Explorer!"
    }
    return render(request, "home.html", context)


def report(request):
    if request.method == "POST":
        # Extract POST data safely
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

    # GET request renders blank form
    return render(request, "report.html")


def search(request):
    # Safely read 'q' query parameter with default fallback to empty string
    query = request.GET.get("q", "").strip()
    
    context = {
        "query": query,
    }
    return render(request, "search.html", context)