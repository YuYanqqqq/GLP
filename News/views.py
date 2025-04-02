from django.shortcuts import render
import erniebot
import json
from django.http import HttpResponse, JsonResponse


def index(request):
    return render(request, 'index.html')


def ask(request):
    # 获取前端发送的问题
    question = request.GET.get('question', '')
    model = request.GET.get('model', 'ernie-3.5-8k')
    print(question)
    print(f"Model: {model}")

    from openai import OpenAI
    client = OpenAI(
        base_url='https://qianfan.baidubce.com/v2',
        api_key='bce-v3/ALTAK-A8Fh3gQJpfddKmC7oeRv2/bff1fd809d83467250acc4ab616be49f978d8f3d'
    )

    # 将文本放在单个消息对象中，用空格分隔不同的文本段落
    message_content = "The task scenario is: I need you to refine the knowledge points I provide into four small modules to help me learn. " \
                      "The best way to refine is to follow a good learning path, and you need to stand from the perspective of a teacher to help me learn the knowledge well. " \
                      f"-对每个模块进行介绍，让读者能够直观的知道该模块的学习内容 我提供的知识点为：{question} " \
                      "-示例json文件如下，参考它的格式：[{\"模块主题\": \"\", \"本模块内容简介\": \"\"},] " \
                      "- Strictly follow the format I provided " \
                      "- 每个模块的介绍在30个中文汉字左右。 " \
                      "- The output is just pure JSON format, with no other descriptions."

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                'top_p': '0.001',
                'content': message_content
            }
        ]
    )
    # 获取文心一言的回答
    print(response)
    answer = response.choices[0].message.content

    print(answer)

    # 解析回答为 Python 字典
    try:
        # 从answer中提取JSON字符串
        json_start = answer.find("[")
        json_end = answer.rfind("]")
        if json_start != -1 and json_end != -1:
            json_content = answer[json_start:json_end + 1]

            # 解析JSON字符串为Python字典
            answer_dict = json.loads(json_content)
        else:
            answer_dict = {}  # 如果找不到JSON内容，则创建一个空字典

    except json.JSONDecodeError:
        answer_dict = {}  # 如果解析失败，则创建一个空字典

    # 提取模块主题和内容简介
    module_titles = []  # 创建一个空列表来存储模块主题和内容简介
    for item in answer_dict:
        module_title = item.get("模块主题", "")
        module_description = item.get("本模块内容简介", "")
        print(module_title)
        print(module_description)
        if module_title and module_description:
            module_titles.append({"模块主题": module_title, "本模块内容简介": module_description})
    # 返回回答给前端
    return JsonResponse(module_titles, safe=False)