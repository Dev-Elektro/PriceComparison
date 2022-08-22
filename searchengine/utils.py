import re
from typing import Iterable


def findPartNumber(query: str) -> str:
    """Поиск парт номера выделенного [] скобками в строке"""
    listRes = re.findall(r'\[([\w-]+)\]', query)
    return None if not listRes else listRes[0]


def wordProcessing(query: str) -> Iterable[str]:
    txt = query.lower().strip() + '\n'
    stopWord = [r'lcd']
    for word in stopWord:
        txt = re.sub(word, '', txt)
    regex = r"([-\da-zA-Z]{2,})[\s|\n]"
    matches = re.findall(regex, txt, re.MULTILINE | re.UNICODE)
    model_pos = 0
    for p, x in enumerate(matches):
        lenW = len(re.findall(r'[a-z]', x))
        lenD = len(re.findall(r'\d', x))
        if lenW > 0 and lenD > 0:
            model_pos = p
            break
    if model_pos > 0:
        model_pos = model_pos - 1 if model_pos == 1 else model_pos - 2
    queryLine = ''
    for x, word in enumerate(matches[model_pos:]):
        queryLine += f"{word.strip()} "
        if len(matches[model_pos:]) == 1:
            yield queryLine.strip()
        if x > 0:
            yield queryLine.strip()
