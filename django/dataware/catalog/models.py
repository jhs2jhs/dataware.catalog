from django.db import models
from django.contrib.auth.models import User

'''
class ResourceRegistration(models.Model):
    STATUS_CHOICES = (
        (-1, 'NOT YET'),
        (0, 'INIT'),
        (1, 'REQUEST'),
        (2, 'REDIRECT'),
        (3, 'GRANT'),
        (4, 'AUTH'),
        (5, 'CONFIRM'),
        (10, 'FINISH'),
        )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    request_token = dwlib.models_type_token()
    user = models.ForeignKey(User, null=True)

    resource_callback = dwlib.models_type_callback()
    resource_temp_id = dwlib.models_type_token()
    resource_access_scope = dwlib.models_type_access_scope()
    
    catalog_callback = dwlib.models_type_callback()
    catalog_temp_id = dwlib.models_type_token()
    catalog_access_scope = dwlib.models_type_access_scope()

    resource_access_token = dwlib.models_type_token()
    resource_validate_code = dwlib.models_type_validate_code()
    
    catalog_access_token = dwlib.models_type_token()
    catalog_validate_code = dwlib.models_type_validate_code()

    def __unicode__(self):
        return self.catalog_callback
'''
