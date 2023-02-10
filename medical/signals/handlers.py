from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from medical.models import Patient

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_patient_for_new_user(sender, **kwargs):
  if kwargs['created']:
    Patient.objects.create(user=kwargs['instance'])