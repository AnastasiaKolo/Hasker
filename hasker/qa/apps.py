from django.apps import AppConfig
# from django.contrib.admin.apps import AdminConfig


class QaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qa'


# class QaAdminConfig(AdminConfig):
#     default_site = "qa.admin.QaAdminSite"
