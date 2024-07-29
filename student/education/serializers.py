from rest_framework import serializers
from .models import Education

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class CreateEducationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
    def create(self,clean_data):
        return Education.objects.create(**clean_data)

class ViewEducationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'

class ViewEducationListSerializer(serializers.Serializer):
    education = ViewEducationSerializer(many = True)
