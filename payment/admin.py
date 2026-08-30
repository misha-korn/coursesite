from django.contrib import admin

from payment.models import BalanceEntry, Payment, Payout

admin.site.register(Payment)
admin.site.register(Payout)
admin.site.register(BalanceEntry)
