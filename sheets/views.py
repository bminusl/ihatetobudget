from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.dates import MonthArchiveView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ihatetobudget.utils.views import InitialDataAsGETOptionsMixin

from .forms import ExpenseForm
from .models import Category, Expense


@login_required
def index(request):
    return render(request, "sheets/index.html")


class SheetView(LoginRequiredMixin, MonthArchiveView):
    template_name = "sheets/sheet.html"
    queryset = Expense.objects.all()
    date_field = "date"
    allow_future = True


class ExpenseCreateView(
    LoginRequiredMixin,
    InitialDataAsGETOptionsMixin,
    SuccessMessageMixin,
    CreateView,
):
    template_name = "sheets/expense/create-update.html"
    form_class = ExpenseForm

    # InitialDataAsGETOptionsMixin
    fields_with_initial_data_as_get_option = [
        (
            "category",
            lambda option_value: Category.objects.get(name=option_value),
        )
    ]

    # SuccessMessageMixin
    success_message = "Expense added!"


class ExpenseUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "sheets/expense/create-update.html"
    model = Expense
    form_class = ExpenseForm

    # SuccessMessageMixin
    success_message = "Expense modified!"


class ExpenseDeleteView(DeleteView):
    #  XXX: a `template_name` must be defined if we want to delete via GET.
    #  Currently, we delete via POST (no need to render a template, since we
    #  redirect).

    model = Expense
    success_url = reverse_lazy("sheets:index")

    # SuccessMessageMixin
    success_message = "Expense deleted!"

    def delete(self, request, *args, **kwargs):
        #  XXX: SuccessMessageMixin not working with DeleteView
        messages.success(self.request, self.success_message)

        super_redirect = super().delete(request, *args, **kwargs)
        object = self.object
        if self.model.objects.filter(
            date__year=object.date.year, date__month=object.date.month
        ).first():
            #  There's a least one other object with the same year and month
            return redirect(object.get_absolute_url())
        return super_redirect


class ExpenseListView(ListView):
    template_name = "sheets/history.html"
    paginate_by = 10
    model = Expense
