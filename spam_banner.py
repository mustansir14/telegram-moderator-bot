from datetime import datetime, timedelta, timezone
from telegram.ext import ContextTypes

# Time span and message count threshold for banning
BAN_TIME_SPAN = 10  # in seconds
BAN_MESSAGE_THRESHOLD = 5
BAN_TIME_PERIOD = 60


class SpamBanner:

    def __init__(self) -> None:

        self.user_messages_times = {}
        self.banned_users = {}

    async def run(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int) -> None:
        self.add_user_message(user_id)

        self.remove_old_messages(user_id)

        if self.has_crossed_rate_limit(user_id):
            await self.ban_user(context, user_id, chat_id)

        await self.unban_expired_users(context, chat_id)

    async def ban_user(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int) -> None:
        await context.bot.ban_chat_member(chat_id, user_id, datetime.now(timezone.utc) + timedelta(minutes=1), True)
        self.banned_users[user_id] = datetime.now()
        self.user_messages_times[user_id] = []
        print("banned", user_id)

    def add_user_message(self, user_id: int) -> None:
        current_time = datetime.now()
        if user_id in self.user_messages_times:
            self.user_messages_times[user_id].append(current_time)
        else:
            self.user_messages_times[user_id] = [current_time]

    def remove_old_messages(self, user_id: int) -> None:

        if user_id not in self.user_messages_times:
            return

        for i in range(len(self.user_messages_times[user_id])):
            if self.user_messages_times[user_id][i] > (datetime.now() - timedelta(seconds=BAN_TIME_SPAN)):
                del self.user_messages_times[user_id][:i]
                break

    def has_crossed_rate_limit(self, user_id: int) -> bool:

        if user_id not in self.user_messages_times:
            return False

        return len(self.user_messages_times[user_id]) >= BAN_MESSAGE_THRESHOLD

    async def unban_expired_users(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:

        user_ids = list(self.banned_users.keys())
        for user_id in user_ids:
            if self.banned_users[user_id] < (datetime.now() - timedelta(seconds=BAN_TIME_PERIOD)):
                await context.bot.unban_chat_member(chat_id, user_id)
                print("unbanned", user_id)
                del self.banned_users[user_id]
