from rest_framework import serializers


class ChoiceStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    votes = serializers.IntegerField()
    percent = serializers.FloatField()


class PollStatsSerializer(serializers.Serializer):
    poll_id = serializers.IntegerField()
    question = serializers.CharField()
    published_at = serializers.DateTimeField()
    total_votes = serializers.IntegerField()
    choices = ChoiceStatsSerializer(many=True)
