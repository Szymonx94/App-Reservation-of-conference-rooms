import datetime

from django.shortcuts import render, redirect
from django.views import View
from .models import Room, RoomReservation


class AddRoom(View):
    def get(self, request):
        return render(request, "add_rooms.html")

    def post(self, request):
        name = request.POST.get("room-name")
        capacity = request.POST.get("capacity")
        capacity = int(capacity) if capacity else 0
        projector = request.POST.get("projector") == "on"

        if not name:
            return render(request, "add_room.html",
                          context={"error": "Room name not entered"})
        if capacity <= 0:
            return render(request, "add_room.html",
                          context={"error": "Room capacity must be a positive number"})
        if Room.objects.filter(name=name).first():
            return render(request, "add_room.html",
                          context={"error": "Room with the given name already exists"})

        Room.objects.create(name=name, capacity=capacity, projector_availability=projector)
        return redirect("/")


class RoomList(View):
    def get(self, request):
        rooms = Room.objects.all()
        for room in rooms:
            reservation_dates = [reservation.date for reservation in room.roomreservation_set.all()]
            room.reserved = datetime.date.today() in reservation_dates
        return render(request, "rooms.html", context={"rooms": rooms})


class DeleteRoom(View):
    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)
        room.delete()
        return redirect("/")


class ModifyRoom(View):
    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)
        return render(request, "modify_room.html", context={"room": room})

    def post(self, request, room_id):
        room = Room.objects.get(id=room_id)
        name = request.POST.get("room-name")
        capacity = request.POST.get("capacity")
        capacity = int(capacity) if capacity else 0
        projector = request.POST.get("projector") == "on"

        if not name:
            return render(request, "modify_room.html",
                          context={"room": room,
                                    "error": "Room name not entered"})
        if capacity <= 0:
            return render(request, "modify_room.html",
                          context={"room": room,
                                    "error": "Room capacity must be a positive number"})
        if name != room.name and Room.objects.filter(name=name).first():
            return render(request, "modify_room.html",
                          context={"room": room,
                                "error": "Room with the given name already exists"})

        room.name = name
        room.capacity = capacity
        room.projector_availability = projector
        room.save()
        return redirect("/")


class Reservation(View):
    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)
        reservations = room.roomreservation_set.filter(date__gte=str(datetime.date.today())).order_by('date')
        return render(request, "reservation.html", context={"room": room, "reservations": reservations})

    def post(self, request, room_id):
        room = Room.objects.get(id=room_id)
        date = request.POST.get("reservation-date")
        comment = request.POST.get("comment")

        reservations = room.roomreservation_set.filter(date__gte=str(datetime.date.today())).order_by('date')

        if RoomReservation.objects.filter(room_id=room, date=date):
            return render(request, "reservation.html", context={"room": room,
                                                                "reservations": reservations,
                                                                "error": "The room has already been booked!"})
        if date < str(datetime.date.today()):
            return render(request, "reservation.html", context={"room": room,
                                                                "reservations": reservations,
                                                                "error": "This is a past date!"})

        RoomReservation.objects.create(room_id=room, date=date, comment=comment)
        return redirect("/")


class RoomDetails(View):
    def get(self, request, room_id):
        room = Room.objects.get(id=room_id)
        reservations = room.roomreservation_set.filter(date__gte=str(datetime.date.today())).order_by('date')
        return render(request, "room_details.html", context={"room": room, "reservations": reservations})


class Search(View):
    def get(self, request):
        name = request.GET.get("room-name")
        capacity = request.GET.get("capacity")
        capacity = int(capacity) if capacity else 0
        projector = request.GET.get("projector") == "on"

        rooms = Room.objects.all()
        if projector:
            rooms = rooms.filter(projector_availability=projector)
        if capacity:
            rooms = rooms.filter(capacity__gte=capacity)
        if name:
            rooms.filter(name__contains=name)

        for room in rooms:
            reservation_dates = [reservation.date for reservation in room.roomreservation_set.all()]
            room.reserved = str(datetime.date.today()) in reservation_dates

        return render(request, "rooms.html", context={"rooms": rooms, "date": datetime.date.today()})
