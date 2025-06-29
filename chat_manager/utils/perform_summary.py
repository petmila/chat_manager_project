import datetime

from utils import summarizer_llm_chain


def perform_summary(messages, chat_id):
    
    queryset = [
        message.format()
        # if message.reply_source_message_id is None
        # else str(message) + str(
        #     models.Message.objects.filter(source_message_id=message.reply_source_message_id).first())
        for message in messages
    ]
    model = summarizer_llm_chain.Summarizer()
    result = model.interact(queryset)
    result = ''.join(result.split('_'))
    return {
        'text': result,
        'date': datetime.date.today(), 'chat': chat_id
    }