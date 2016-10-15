from django.contrib import admin

from .models import Credential, ForceObj, ForceField


def refresh_salesforce_objects(modeladmin, request, queryset):
    for obj in queryset:
        obj.get_objects()
refresh_salesforce_objects.short_description = 'Refresh SF Objects'

class CredentialAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user_id',)
            }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('password','user_token','consumer_key',
                'consumer_secret','request_token_url',
                'access_token_url','http_proxy','https_proxy')
            }),
        )
    list_display = ('user_id', 'has_objects')
    actions = [refresh_salesforce_objects]


def describe_object(modeladmin, request, queryset):
    for obj in queryset:
        obj.get_description()
describe_object.short_description = 'Get SF Fields'

def toggle_commonly_used(modeladmin, request, queryset):
    for obj in queryset:
        cu = obj.commonly_used
        obj.commonly_used = not(cu)
        obj.save()
toggle_commonly_used.short_description = 'Toggle Commonly Used'


class ForceObjAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'has_description', 'commonly_used')
    actions = [toggle_commonly_used, describe_object]


admin.site.register(Credential, CredentialAdmin)
admin.site.register(ForceObj, ForceObjAdmin)
admin.site.register(ForceField)
