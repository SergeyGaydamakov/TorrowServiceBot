from environment import OPENAI_API_KEY, BASE_URL, GPT_MODEL, TELEGRAM_TOKEN
from termcolor import colored 
import typing
from openai import OpenAI
import json
from datetime import datetime
from dateutil.parser import parse
from collections.abc import Iterable

class BaseTote():
    def __init__(self):
        return

    def name(self) -> str:
        return "BaseTote"

    def test1(self) -> float:
        return 0.0

    def operation(self):
        return

    def test2(self) -> bool:
        return true

    def exit(self):
        return

type BaseToteList = BaseTote[int]
type BaseToteDict = dict(BaseTote)

class ToteContext:
    _tote_dict: BaseToteDict = None

    def __init__(self):
        self._tote_dict = {}

    def add_tote(self, tote: BaseTote) -> BaseTote:
        self._tote_dict[tote.name] = tote
        return tote

    def remove_tote(self, tote: BaseTote) -> BaseTote:
        found_tote = self._tote_dict.get(tote.name)
        if (found_tote):
            del self._tote_dict[tote.name]
        return found_tote

    def get_tote_list(self) -> BaseToteList:
        return self._tote_dict.values()

    def is_empty(self) -> bool:
        return len(self._tote_dict.count) == 0

type ToteMessageList = list()
class ToteMessages:
    _list: ToteMessageList = None

    def __init__(self):
        self._list = []

    def add_message(self, role: str, content: str) -> ToteMessageList:
        self._list.append({"role": role, "content": content})
        return self._list

    def get_list(self) -> ToteMessageList:
        return self._list
    
    def clear(self):
        self._list.clear()

class ContextedTote(BaseTote):
    _context: ToteContext = None
    def __init__(self, context):
        super().__init__()
        self._context = context
        self._context.add_tote(self)

    def exit(self):
        # Требуется удалить TOTE из контекста TOTE-ов
        self._context.remove_tote(self)
        super().exit()
        return

class ToteCommunication():
    """ Управляющий Tote-ами класс """
    _context: ToteContext = None
    _last_tote: BaseTote = None
    _count_last_tote: int = 0

    def __init__(self, context: ToteContext):
        self._context = context

    def set_next_tote(self, new_tote: BaseTote) -> BaseTote:
        if new_tote:
            print(colored("New Tote = "+new_tote.name(), "green"))
        else:
            print(colored("Empty new Tote", "green"))
        #self._current_tote = new_tote
        #return self._current_tote

    def do(self) -> bool:
        if not self._context:
            return False
        preffered_tote: BaseTote = None
        preffered_tote_test1: float = 0.0    
        # Поиск Tote с максимальным test1
        for tote in self._context.get_tote_list():
            print(colored(tote.name(), "green"))
            test1: float = tote.test1()
            if preffered_tote == None and test1 > 0.0:
                preffered_tote = tote
            elif  test1 > preffered_tote_test1:
                preffered_tote = tote
                preffered_tote_test1 = test1
        if not preffered_tote:
            return False
        # Защита от зацикливания на одном и том же Tote
        if (self._last_tote != None) and (self._last_tote.name() == preffered_tote.name()):
            self._count_last_tote += 1
            if self._count_last_tote > 10:
                print(colored("Остановка на Tote = " + self._current_tote.name(), "red"))
                return False
        # Tote найден, его нужно выполнить
        print(colored("["+preffered_tote.name()+"] Tote.operation","green"))
        preffered_tote.operation()
        # Проверка завершения Tote и его удаление из контекста
        test2 = preffered_tote.test2()
        print(colored("["+preffered_tote.name()+"] Tote.test2 = "+str(test2),"green"))
        if test2:
            self._context.remove_tote(preffered_tote)
            print(colored("["+preffered_tote.name()+"] Tote.exit","green"))
            preffered_tote.exit()
        if not self._last_tote or self._last_tote.name() != preffered_tote.name():
            self._count_last_tote = 0
            self._last_tote = preffered_tote
        return True

    def process(self):
        step = 0
        while self.do():
            step += 1
            print("step ", step)

type OpenAI_ChatCompletionMessage = OpenAI.ChatCompletionMessage

class OpenAITote(ContextedTote):
    _openai_client = None
    _chat_messages = []
    _is_conversation = None

    def __init__(self, context, openai_client, messages):
        super().__init__(context)
        self._openai_client = openai_client
        self._chat_messages = messages
        self._is_conversation = True

    def _add_message(self, role, content):
        message = {"role": role, "content": content}
        self._chat_messages.append(message)

    def _pretty_print_conversation(self, messages):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        for message in messages:
            if message["role"] == "system":
                print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
            elif message["role"] == "user":
                print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
            elif message["role"] == "assistant" and message.get("function_call"):
                print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
            elif message["role"] == "assistant" and not message.get("function_call"):
                print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
            elif message["role"] == "function":
                print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

    def complete_conversation(self):
        self._is_conversation = False
        print(colored("[" + self.name() + "] Разговор завершен", "green"))

    def _get_chat_messages(self):
        """Сообщения для AI"""
        return self._chat_messages

    def _get_tools(self):
        return None

    def _chat_completion_request(self):
        model = 'gpt-3.5-turbo-1106'
        try:
            messages = self._get_chat_messages()
            print(colored(messages, "red"))
            response: ChatCompletion = None
            response = self._openai_client.chat.completions.create(
                model= model,
                frequency_penalty = 0.0,
                presence_penalty = 0.0,
                messages= messages,
                tools= self._get_tools(),
                response_format= { "type": "text" },
                temperature= 0.2
            )
            print(colored(response,"grey"))
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return None

    def _tools_execute(self, full_message: OpenAI_ChatCompletionMessage) -> str:
        return None

    def operation(self):
        response: OpenAI.ChatCompletion
        response = self._chat_completion_request()
        if (response == None):
            self.complete_conversation()
            return
        full_message: OpenAI.ChatCompletionMessage
        full_message = response.choices[0].message
        if (response.choices[0].finish_reason == "tool_calls"):
            result = self._tools_execute(full_message)
            if result:
                message = {
                        "role": "function",
                        "tool_call_id": full_message.tool_calls[0].id, 
                        "name": full_message.tool_calls[0].function.name,
                        "content": str(result),
                    }
                #print(colored(message, "grey"))
                self._chat_messages.append(message)
        else:
            print(colored(full_message.content,"grey"))
            user_message = input()
            self._add_message("user", user_message)

    def test2(self) -> bool:
        return not self._is_conversation

    def exit(self):
        super().exit()
        return


class ChooseTimeTote( OpenAITote ):
    _choosen_time = None
    _tote_messages: ToteMessages = None

    def __init__(self, context: ToteContext, openai_client, tote_messages: ToteMessages):
        self._choosen_time = None
        self._tote_messages = tote_messages
        messages = []
        messages.append({"role": "system", "content": "Не делай предположений о том, какие значения следует передавать в функцию. Попроси разъяснений, если запрос пользователя неоднозначен. Пользователь должен выбрать дату и время из ограниченного списка свободных дат и времени. Если свободного времени много, то сгруппируй его по датам."})
        messages.append({"role": "user", "content": "Я хочу записаться на свободную дату и время"})
        super().__init__(context, openai_client, messages)

    def _get_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_available_time",
                    "description": "Используй эту функцию, чтобы получить список свободного времени для записи на услугу"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_choosen_time",
                    "description": "Используй эту функцию, чтобы сохранить выбранное пользователем дату и время из списка свободного",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "choosen_time": {
                                "type": "string",
                                "description": "Выбранное пользователем дата и время формате dd.mm.yyyy hh:mm, например 12.03.2024 10:00",
                            }
                        },
                        "required": ["choosen_time"]
                    },
                }
            },
        ]

    def _get_available_time(self):
        print(colored("Запрошено доступное время записи", "blue"))
        POSSIBLE_DATES = ["10.03.2024 10:00", "10.03.2024 11:00", "10.03.2024 12:00", "10.03.2024 13:00", "11.03.2024 10:00", "11.03.2024 11:00", "11.03.2024 12:00", "12.03.2024 10:00", "12.03.2024 11:00", "12.03.2024 12:00", "14.03.2024 10:00", "14.03.2024 11:00", "14.03.2024 12:00"]
        return ", ".join(POSSIBLE_DATES)

    def _set_choosen_time(self, choosen_time):
        try:
            self._choosen_time = datetime.strptime(choosen_time, "%d.%m.%Y %H:%M")
            #self._choosen_time = parse(choosen_time)
            print(colored("Выбрано время: " + self._choosen_time.strftime("%d.%m.%Y %H:%M"), "blue"))
            if self._tote_messages:
                self._tote_messages.clear()
                self._tote_messages.add_message(role="assistant", content="Пользователь выбрал дату и время "+self._choosen_time.strftime("%d.%m.%Y %H:%M"))
        except ValueError:
            self._choosen_time = None
            print(colored("Указано время некорректном формате: " + choosen_time, "blue"))
        return choosen_time

    def _tools_execute(self, full_message: OpenAI_ChatCompletionMessage) -> str:
        result: str = ""
        if full_message.tool_calls[0].function.name == "get_available_time":
            results = self._get_available_time()
        elif full_message.tool_calls[0].function.name == "set_choosen_time":
            choosen_time = json.loads(full_message.tool_calls[0].function.arguments)["choosen_time"]
            results = self._set_choosen_time(choosen_time)
        else:
            results = f"Error: function {full_message.tool_calls[0].function.name} does not exist"
        return results
        
    @typing.override
    def name(self) -> str:
        return "ChooseTimeTote"

    @typing.override
    def test1(self) -> float:
        return 2.0

    @typing.override
    def operation(self):
        super().operation()

    @typing.override
    def test2(self) -> bool:
        return super().test2() or (self._choosen_time != None)

    @typing.override
    def exit(self):
        super().exit()
        return


class ServiceTote( OpenAITote ):
    _choose_time_messages: ToteMessages = None

    def __init__(self, context, openai_client):
        self._choosen_time = None
        self._choose_time_messages = ToteMessages()
        messages = []
        messages.append({"role": "system", "content": "Используй функции по назначению. Тебе нужно записать пользователя на услугу, для этого нужно получить от пользователя дату и время."})
        messages.append({"role": "user", "content": "Я хочу записаться на услугу Стрижка"})
        super().__init__(context, openai_client, messages)

    def _get_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "_choose_time",
                    "description": "Используй эту функцию, чтобы получить время записи на услугу"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "_complete",
                    "description": "Используй эту функцию, когда получишь всю информацию для записи на услугу"
                }
            },
        ]

    def _get_chat_messages(self):
        """Сообщения для AI"""
        return self._chat_messages + self._choose_time_messages.get_list()

    def _choose_time(self) -> str:
        print(colored("Выбор времени", "blue"))
        ChooseTimeTote(context=self._context, openai_client=self._openai_client, tote_messages=self._choose_time_messages)
        return None

    def _complete(self):
        self.complete_conversation()
        return

    def _tools_execute(self, full_message: OpenAI_ChatCompletionMessage) -> str:
        if full_message.tool_calls[0].function.name == "_choose_time":
            results = self._choose_time()
        elif full_message.tool_calls[0].function.name == "_complete":
            #choosen_time = json.loads(full_message.tool_calls[0].function.arguments)["choosen_time"]
            results = self._complete()
        else:
            results = f"Error: function {full_message.tool_calls[0].function.name} does not exist"
        return results
        
    @typing.override
    def name(self) -> str:
        return "ServiceTote"

    @typing.override
    def test1(self) -> float:
        return 1.0

    @typing.override
    def operation(self):
        super().operation()

    @typing.override
    def test2(self) -> bool:
        return super().test2()

    @typing.override
    def exit(self):
        super().exit()
        return


def main():
    # Это купленный ключ ProxiApi
#    OPENAI_API_KEY = 'sk-KL9IAgVMN0oSEuH9ixzacOFR2dJLUMpc'
#    BASE_URL = "https://api.proxyapi.ru/openai/v1"
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=BASE_URL
    )
    messages =[]
    messages.append({"role": "system", "content": "Не делай предположений о том, какие значения следует передавать функцию. Попроси разъяснений, если запрос пользователя неоднозначен. Выясни на какое свободное время записать пользователя."})
    messages.append({"role": "user", "content": "Какое время свободно для записи на услугу?"})
    context = ToteContext()
    ChooseTimeTote(context=context, openai_client=client, tote_messages=None)
#    ServiceTote(context=context, openai_client=client)
    ToteCommunication(context).process()    

if __name__ == '__main__':
    main()
