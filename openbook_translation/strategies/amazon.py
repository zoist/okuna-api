from openbook_translation.strategies.base import BaseTranslationStrategy, MaxTextLengthExceededError, \
    TranslationClientError, UnsupportedLanguagePairException
from django.conf import settings
from langdetect import DetectorFactory, detect
import boto3
from botocore.exceptions import ClientError

# seed the language detector
DetectorFactory.seed = 0


class AmazonTranslate(BaseTranslationStrategy):

    client = boto3.client(service_name='translate', region_name=settings.AWS_TRANSLATE_REGION, use_ssl=True)

    def get_detected_language_code(self, text):
        # amazons translate API codes as stored in the languages.json are slightly different
        # from what langdetect provides for chinese (zh) and chinese traditional (zh-TW)

        detected_language = detect(text)
        if detected_language is 'zh-cn':
            detected_language = 'zh'
        if detected_language is 'zh-tw':
            detected_language = 'zh-TW'

        return detected_language

    def translate_text(self, text, source_language_code, target_language_code):

        if len(text) > self.text_max_length:
            raise MaxTextLengthExceededError('MaxTextLengthExceededError')

        try:
            response = self.client.translate_text(Text=text,
                                                  SourceLanguageCode=source_language_code,
                                                  TargetLanguageCode=target_language_code)
        except self.client.exceptions.UnsupportedLanguagePairException as e:
            print('Client error from AWS Translate : \n %s' % e)
            raise UnsupportedLanguagePairException
        except ClientError as e:
            print('Client error from AWS Translate : \n %s' % e)
            raise TranslationClientError

        result = {
            'translated_text': response.get('TranslatedText'),
            'source_language_code': response.get('SourceLanguageCode'),
            'target_language_code': response.get('TargetLanguageCode')
        }

        return result
