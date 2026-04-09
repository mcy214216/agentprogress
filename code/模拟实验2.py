# -*- coding: utf-8 -*-
# 时间 : 2026/4/9 08:55
# 作者 : mcy
# 文件 : 模拟实验2.py


import requests
from pydantic import Field
# 定义心知天气API的工具类
class WeatherTool:
    city: str = Field(description="City name, include city and county")
    def __init__(self, api_key) -> None:
        self.api_key = api_key
    def run(self, city):
        city = city.split("\n")[0] # 清除多余的换行符，避免报错
        url = f"https://api.seniverse.com/v3/weather/now.json?key={self.api_key}&location={city}&language=zh-Hans&unit=c"
        # 构建 API 请求 URL 返回结果
        response = requests.get(url)
        if response.status_code == 200: # 请求成功
            data = response.json() # 解析返回的JSON
            weather = data["results"][0]["now"]["text"] # 天气信息
            tem = data["results"][0]["now"]["temperature"] # 温度
            return f"{city}的天气是{weather}, 温度是{tem}°C"  # 返回格式化后的天气信息
        else:
            return f"无法获取{city}的天气信息。"
api_key = "SHz8d4ru_U0Zbg7Bb"
weather_tool = WeatherTool(api_key)
# print(weather_tool.run("成都"))

from langchain_openai import ChatOpenAI
chat_model = ChatOpenAI(
    openai_api_key="ollama",
    base_url="http://localhost:11434/v1",
    model="qwen2.5:7b"
)

from langchain.agents import Tool # 用于封装工具
# 将API工具封装成langchain的TOOL对象
tools = [Tool(
        name="weather check", # 工具名称
        func=weather_tool.run, # 触发测具体函数
        description="检查制定城市的天气情况。"
        )]

from langchain_core.prompts import PromptTemplate
template = """请尽可能好地回答以下问题。如果需要，可以适当的使用一些功能。
    你有以下工具可用：\n
    {tools}\n
    请使用以下格式： \n
    Question: 需要回答的问题。\n
    Thought: 总是考虑应该做什么以及使用哪些工具。\n
    Action: 应采取的行动，应为 [{tool_names}] 中的一个。\n
    Action Input: 行动的输入。\n
    Observation: 行动的结果。\n
    ... (这个 Thought/Action/Action Input/Observation 过程可以重复零次或者多次)。\n
    Thought: 我现在知道最终答案了。\n
    Final Answer: 对原问题的最终答案。\n
    开始！ \n
    Quesion: {input}\n
    Thought: {agent_scratchpad}\n
    """

prompt = PromptTemplate.from_template(template)
# 导入 代理创建函数 和 代理执行器
from langchain.agents import create_react_agent, AgentExecutor
agent = create_react_agent(chat_model, tools, prompt, stop_sequence=["\nObservation:"])
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True ,handle_parsing_errors=True)


query = "成都天气怎么样"
response = agent_executor.invoke({"input": query})
print(response)
query = "北京天气怎么样"
response = agent_executor.invoke({"input": query})
print(response)




























