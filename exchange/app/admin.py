from django.contrib import admin
from .models import Profile,Order,Transaction,Bank
from django.contrib.auth.models import User 

# Register your models here.

class ProfileAdmin(admin.TabularInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileAdmin ]

class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ["placer","type","amount","USDprice","status" ,"datetime" ]#,"fulfiller",

class TrasactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = ["sender","receiver","type","USDprice","amount","datetime",]

class BankAdmin(admin.ModelAdmin):
    model = Bank
    list_display =["currency","treasure","treasureUSD"]#"orders_pool","trasnsactions_pool"]
 

admin.site.register(Profile)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Transaction,TrasactionAdmin)
admin.site.register(Bank,BankAdmin)