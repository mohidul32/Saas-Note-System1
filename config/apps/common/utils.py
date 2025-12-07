from django.utils.text import slugify
import uuid


def generate_unique_slug(instance, base_slug=None, field_name='slug'):
    """Generate a unique slug for a model instance"""
    if base_slug is None:
        base_slug = slugify(getattr(instance, 'name', str(uuid.uuid4())))

    slug = base_slug
    model_class = instance.__class__
    counter = 1

    while model_class.objects.filter(**{field_name: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug