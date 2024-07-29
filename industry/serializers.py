from rest_framework import serializers
from .models import PartnerDetails, JobDescription


class CreatePartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerDetails
        fields = ["id", "user", "company"]

    def create(self, clean_data):
        return PartnerDetails.objects.create(**clean_data)


class CreateJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = "__all__"

    def create(self, clean_data):
        return JobDescription.objects.create(**clean_data)


class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = "__all__"


class ViewAllJobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = "__all__"


class ViewAllJobsListSerializer(serializers.Serializer):
    jobs = ViewAllJobsSerializer(many=True)
