import datetime

from utils import saiga_llm_chain


def perform_summary(chat_id, first_date, last_date):
    from manager_app import models
    chat = models.Chat.objects.filter(id=chat_id).first()
    messages = models.Message.objects.filter(chat=chat,
                                             timestamp__range=(first_date, last_date)).order_by('timestamp')
    queryset = [
        str(message)
        # if message.reply_source_message_id is None
        # else str(message) + str(
        #     models.Message.objects.filter(source_message_id=message.reply_source_message_id).first())
        for message in messages
    ]
    model = saiga_llm_chain.SaigaModel()
    result = model.interact('-'.join(queryset))

    return {
        'text': result,
        'date': datetime.date.today(), 'chat': chat.id
    }