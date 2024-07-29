from rest_framework import serializers

from .models import AppliedToJob
from industry.models import JobDescription


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ApplyForProjectSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = AppliedToJob
        fields = "__all__"

    def create(self, clean_data):
        return AppliedToJob.objects.create(**clean_data)


class ViewAllJobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = "__all__"
