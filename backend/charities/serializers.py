from rest_framework import serializers

from .models import Charity, Task, Benefactor


class BenefactorSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        serializer = Benefactor.objects.create(**validated_data)
        serializer.save()
        return serializer

    class Meta:
        model = Benefactor
        fields = (
            'experience',
            'free_time_per_week',
        )


class CharitySerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        serializer = Charity.objects.create(**validated_data)
        serializer.save()
        return serializer

    class Meta:
        model = Charity
        fields = (
            "name",
            "reg_number",
        )


class TaskSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(read_only=True, choices=Task.TaskStatus.choices)
    assigned_benefactor = BenefactorSerializer(required=False)
    charity = CharitySerializer(read_only=True)
    charity_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Charity.objects.all(), source='charity')

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'state',
            'charity',
            'charity_id',
            'description',
            'assigned_benefactor',
            'date',
            'age_limit_from',
            'age_limit_to',
            'gender_limit',
        )
