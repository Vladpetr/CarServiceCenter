from django.views import View
from django.shortcuts import render, redirect
from collections import deque


class WelcomeView(View):
    def get(self, request, *args, **kwargs):

        return render(request, 'tickets/welcome.html')


class MenuView(View):
    template_name = 'tickets/menu.html'
    menu = {
        "change_oil": "Change oil",
        "inflate_tires": "Inflate tires",
        "diagnostic": "Get diagnostic test",
    }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={'menu': self.menu})


tickets = {'change_oil': deque(), 'inflate_tires': deque(), 'diagnostic': deque()}


class TicketView(View):

    template = 'tickets/ticket.html'
    customers = []

    def get(self, request, service_type, *args, **kwargs):
        if service_type == 'change_oil':
            minutes_to_wait = 2 * len(tickets['change_oil'])
        elif service_type == 'inflate_tires':
            minutes_to_wait = 2 * len(tickets['change_oil']) + 5 * len(tickets['inflate_tires'])
        else:
            minutes_to_wait = 2 * len(tickets['change_oil']) + 5 * len(tickets['inflate_tires']) + 30 * len(tickets['diagnostic'])

        self.customers.append(request.user)
        ticket_number = len(self.customers)
        tickets[service_type].append(ticket_number)
        context = {'ticket_number': ticket_number, 'minutes_to_wait': minutes_to_wait}

        return render(request, self.template, context=context)


helper = deque()


class ProcessingView(View):

    def get(self, request, *args, **kwargs):
        template_name = 'tickets/processing.html'
        return render(request, template_name, context={'tickets': tickets})

    def post(self, request, *args, **kwargs):
        if helper:
            helper.popleft()
        if tickets['change_oil']:
            helper.append(tickets['change_oil'].popleft())
        elif tickets['inflate_tires']:
            helper.append(tickets['inflate_tires'].popleft())
        elif tickets['diagnostic']:
            helper.append(tickets['diagnostic'].popleft())
        return redirect('/next')


class NextView(View):
    template = 'tickets/next.html'

    def get(self, request, *args, **kwargs):
        if helper:
            info = f'Next ticket #{helper[0]}'
        else:
            info = 'Waiting for the next client'
        return render(request, self.template, context={'info': info})



