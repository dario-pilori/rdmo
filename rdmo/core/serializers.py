from markdown import markdown as markdown_function

from django.conf import settings
from django.utils.encoding import force_text

from rest_framework import serializers

from rdmo.core.constants import LANGUAGE_RANGE


class RecursiveField(serializers.Serializer):

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ChoicesSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj[0]

    def get_text(self, obj):
        return obj[1]


class MarkdownSerializerMixin(serializers.Serializer):

    markdown_fields = ()

    def to_representation(self, instance):
        response = super(MarkdownSerializerMixin, self).to_representation(instance)

        for markdown_field in self.markdown_fields:
            if markdown_field in response and response[markdown_field]:
                response[markdown_field] = markdown_function(force_text(response[markdown_field]))

        return response


class TranslationSerializerMixin(object):

    def __init__(self, *args, **kwargs):
        super(TranslationSerializerMixin, self).__init__(*args, **kwargs)

        meta = getattr(self, 'Meta', None)

        if meta:
            for i in LANGUAGE_RANGE:
                try:
                    lang_code, lang = settings.LANGUAGES[i]

                    for field in meta.trans_fields:
                        self.fields['%s_%s' % (field, lang_code)] = serializers.CharField(source='%s_lang%i' % (field, i + 1))

                except IndexError:
                    break
