from django.db import models


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """Abstract base model for soft deletion."""
    is_deleted = models.BooleanField(default=False, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Manager to access all objects, including deleted ones

    def delete(self):
        """Soft delete the object by setting is_deleted to True."""
        self.is_deleted = True
        self.save()

    def hard_delete(self):
        """Hard delete the object from the database."""
        super().delete()

    class Meta:
        abstract = True
