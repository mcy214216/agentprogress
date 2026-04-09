# -*- coding: utf-8 -*-
# 时间 : 2026/4/9 10:09
# 作者 : mcy
# 文件 : 实验.py

#调用库
import requests
from pydantic import Field
from typing import Optional
from datetime import datetime

from langchain_openai import ChatOpenAI #调用模型
from langchain.agents import Tool #调用工具
import json
from langchain_core.prompts import PromptTemplate #定义 ReAct 风格的提示模板
from langchain.agents import create_react_agent, AgentExecutor #创建 ReAct 代理及代理执行器
#定义工具类api
#分别是心知天气API、ai万能翻译API、历史上的今天
## 心知天气API
class WeatherTool:
    city: str = Field(description="City name, include city and county")
    def __init__(self, api_key) -> None:
        self.api_key = api_key
    def run(self, city):
        if isinstance(city, dict):
            city = city.get("city", "")
        elif isinstance(city, str):
            # 尝试去掉首尾空格，如果是 JSON 字符串则解析
            stripped = city.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                try:
                    city = json.loads(stripped).get("city", city)
                except:
                    pass
            # 无论是否解析，都清除换行符

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


class TranslateTool:
    text: str = Field(description="Text to be translated, support multiple languages")
    def run(self, text: str) -> str:
        """执行翻译，返回翻译后的文本"""
        text = text.split("\n")[0]  # 清除换行符
        try:
            resp = requests.post(
                "https://api.pearktrue.cn/api/translate/ai/",
                data={"text": text},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data") if data.get("code") == 200 else f"翻译失败: {data.get('msg')}"
            return f"HTTP错误: {resp.status_code}"
        except Exception as e:
            return f"请求异常: {e}"
translate_tool = TranslateTool()

class HistoryTool:
    date: Optional[str] = Field(None, description="Date (YYYY-MM-DD). Uses today if omitted.")

    def run(self, date: Optional[str] = None) -> str:
        date = date or datetime.now().strftime("%Y-%m-%d")
        date = date.split("\n")[0]
        try:
            resp = requests.get(
                "https://api.pearktrue.cn/api/lsjt/",
                params={"date": date},
                timeout=10
            )
            if resp.status_code == 200:
                raw_text= resp.text
                lines = [line.strip() for line in raw_text.strip().split('\n') if line.strip()]
                # 格式化返回结果，每行事件前面加序号
                formatted_result = f"历史上的{date}（基于现有数据）发生的事件：\n"
                for i, line in enumerate(lines, 1):
                    formatted_result += f"{i}. {line}\n"
                return formatted_result
            else:
                return f"HTTP错误: {resp.status_code}"
        except Exception as e:
            return f"请求异常: {e}"
history_tool = HistoryTool()
#调用模型
chat_model = ChatOpenAI(
    openai_api_key="ollama",
    base_url="http://localhost:11434/v1",
    model="qwen2.5:7b"
)

#将工具封装成 LangChain Tool 对象
tools = [Tool(
        name="weather check", # 工具名称
        func=weather_tool.run, # 触发测具体函数
        description="检查制定城市的天气情况。"
        ),
         Tool(
        name="ai万能翻译",
        func=translate_tool.run,
        description="翻译任意语言。"
        ),
          Tool(
        name="历史上的今天",
        func=history_tool.run,
        description="查询历史上的今天。"
        )

]

#定义 ReAct 风格的提示模板
REACT_PROMPT = """你是一个智能助手，可以调用外部工具来回答问题。你有以下工具可用：

{tools}

工具名称：{tool_names}

请严格按照以下格式进行推理和行动：

Question: 用户的问题
Thought: 你应该思考下一步该做什么。
Action: 要调用的工具名称，必须是 [{tool_names}] 中的一个。
Action Input: 调用工具时传入的参数，是一个合法的 JSON 字符串。
Observation: 工具返回的结果
...（这个 Thought/Action/Action Input/Observation 可以重复多次）
Thought: 我现在知道最终答案了。
Final Answer: 对用户的最终回答

开始！

Question: {input}
{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(REACT_PROMPT)
#创建 ReAct 代理及代理执行器
agent = create_react_agent(chat_model, tools, prompt, stop_sequence=["\nObserv"])
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True ,handle_parsing_errors=True)


while True:
    query = input("\n请输入问题（输入 exit 退出）：")
    if query.strip() == "exit":
        break
    try:
        response = agent_executor.invoke({"input": query})
        print("\n" + response["output"])
    except Exception as e:
        print(f"处理出错：{e}")