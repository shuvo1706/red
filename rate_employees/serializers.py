from rest_framework import serializers
from .models import Award

class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ('advisorid', 'award_evaluatorid', 'award_evaluateeid','purposeid','description','Status', 'remark')
