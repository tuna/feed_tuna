from telegram.ext import Handler
from telegram import Update

class PaymentHandler(Handler):

    def __init__(self,
                 callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        super(PaymentHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)
        self.type = None

    def check_update(self, update):
        # This method is called to determine if an update should be handled by this handler instance.
        if not isinstance(update, Update):
            return False
        if update.shipping_query:
            return True
        if update.pre_checkout_query:
            return True
        if update.message or update.edited_message:
            return update.message.successful_payment is not None

    def handle_update(self, update, dispatcher):
        return self.callback(dispatcher.bot, update)

class BrowersHandler(Handler):

    def __init__(self,
                 callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        super(BrowersHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)
        self.type = None

    def check_update(self, update):
        # This method is called to determine if an update should be handled by this handler instance.
        if not isinstance(update, Update):
            return False
        if update.callback_query:
            return True

    def handle_update(self, update, dispatcher):
        return self.callback(dispatcher.bot, update)
