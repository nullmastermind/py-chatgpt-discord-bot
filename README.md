# Please use https://gpt.dongnv.dev instead. repo: https://github.com/nullmastermind/chatgpt-web





# ChatGPT Discord Bot: **Fast. No daily limits. Special chat modes**

```diff
+ I am very interested in this repository, so you don't need to worry if there
+ hasn't been an update for a while. Simply put, it is still functioning stably
+ without the need for updates.
```

If you need an additional bot on Telegram, you may like this repository: https://github.com/karfly/chatgpt_telegram_bot

Discord BOT: NullGPT#0657 https://discord.gg/kCwPAGj9Rc

## Features

- Low latency replies
- No request limits
- Message streaming
- Code highlighting
- Special chat modes. You can easily create your own chat modes by editing `config.py`
- The program is lightweight and compact, simply a Python script without any accompanying database or other components.
- The software has a high level of customization, allowing you to adjust the "temperature" or use a quick selection button for "temperature" if you are not satisfied with the result.
- Use the "history: number_of_last_messages" option to utilize chat history only when necessary.

## Setup

- To run a local test, simply create a `.env` file and copy the content of the `.env.example` file over. Please note that you need to fill in the API KEY completely. `python main.py`
- To run on Docker, you need to modify the environment variables in the `docker-compose.yml` file and then run `docker-compose up --build -d`.

## Roadmap

- [x] Special chat modes
- [ ] Integrate the features of Langchain (https://github.com/hwchase17/langchain) to produce more complex results.

## Bot commands:

- /code
- /assistant
- /english_translator
- /english_translator_technical
- /english_teacher
- /text_improver
- /show_history <number_of_last_messages>
- /regenerate: Regenerate the answer with customizable options that can be modified
- /estimate: Task estimate assistant
- /midjourney: Expand your midjourney ideas

You can easily add or delete as desired in [config.py](https://github.com/nullmastermind/py-chatgpt-discord-bot/blob/master/config.py)

## Options:

- continue_conv <True/False>: Whether to continue the previous conversation
- prompt: required
- temperature: The temperature to use for message generation. Default in config.py
- history: default 0. If this option is used, it will disable the 'continue_conv' option.
- max_tokens: default 1000

## Youtube video

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/ZwSu8f1DKmI/0.jpg)](https://www.youtube.com/watch?v=ZwSu8f1DKmI)
