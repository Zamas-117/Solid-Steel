from django.db import models


class DatosRetiro(models.Model):
    nombre_titular = models.CharField(max_length=100)
    cuenta_paypal = models.EmailField()

    def __str__(self):
        return f"{self.nombre_titular} - {self.cuenta_paypal}"
