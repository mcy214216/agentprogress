# import requests
# import json
#
# class PearkTrueTranslator:
#     def __init__(self, base_url="https://api.pearktrue.cn/api/translate/ai/"):
#         self.base_url = base_url
#         self.session = requests.Session()
#         self.session.headers.update({
#             "User-Agent": "Mozilla/5.0 (compatible; MyTranslator/1.0)"
#         })
#
#     def translate(self, text, source_lang=None, target_lang=None):
#         """
#         调用AI翻译API
#         :param text: 待翻译的文本（必填）
#         :param source_lang: 源语言代码（可选，API可能自动检测）
#         :param target_lang: 目标语言代码（可选，API可能默认中文）
#         :return: 翻译后的字符串，失败返回None
#         """
#         payload = {"text": text}
#         # 如果提供了语言参数，也加入请求（API可能支持）
#         if source_lang:
#             payload["from"] = source_lang
#         if target_lang:
#             payload["to"] = target_lang
#
#         try:
#             resp = self.session.post(self.base_url, data=payload, timeout=10)
#             resp.raise_for_status()
#             data = resp.json()
#
#             # 根据探测到的成功响应格式解析
#             if data.get("code") == 200:
#                 return data.get("data")   # data 字段直接就是翻译结果字符串
#             else:
#                 print(f"翻译失败: {data.get('msg')}")
#                 return None
#
#         except Exception as e:
#             print(f"请求异常: {e}")
#             return None
#
# # 使用示例
# if __name__ == "__main__":
#     translator = PearkTrueTranslator()
#     result = translator.translate("Hello world", source_lang="en", target_lang="zh")
#     print("翻译结果:", result)   # 输出: 你好世界

import requests
from pydantic import Field


# class TranslateTool:
#     text: str = Field(description="Text to be translated, support multiple languages")
#
#     def run(self, text: str) -> str:
#         """执行翻译，返回翻译后的文本"""
#         text = text.split("\n")[0]  # 清除换行符
#         try:
#             resp = requests.post(
#                 "https://api.pearktrue.cn/api/translate/ai/",
#                 data={"text": text},
#                 timeout=10
#             )
#             if resp.status_code == 200:
#                 data = resp.json()
#                 return data.get("data") if data.get("code") == 200 else f"翻译失败: {data.get('msg')}"
#             return f"HTTP错误: {resp.status_code}"
#         except Exception as e:
#             return f"请求异常: {e}"
#
# tool = TranslateTool()
# result = tool.run("Hello world")
# print(result)  # 你好世界
from typing import Optional
from datetime import datetime
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
tool=HistoryTool()
result =tool.run()
print(result)