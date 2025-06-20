from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Button:
    name: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None

    def asdict(self):
        result = {}
        if self.name:
            result['name'] = str(self.name)
        result["type"] = "button"
        if self.url:
            result['integration'] = {
                "url": str(self.url),
                "context": {}
            }
            if self.text:
                result['integration']['context']['text'] = str(self.text)
        return result


@dataclass
class Keyboard:
    channel_id: Optional[str] = None
    message: Optional[str] = None
    buttons: Optional[List[Button]] = None

    def asdict(self):
        result = {}
        if self.buttons:
            result['props'] = {
                "attachments": [{
                    "actions": [button.asdict() for button in self.buttons]
                }]
            }
        if self.channel_id:
            result['channel_id'] = str(self.channel_id)
        if self.message:
            result['message'] = str(self.message)

        return result

@dataclass
class Option:
    text: Optional[str] = None
    value: Optional[str] = None

    def asdict(self):
        result = {}
        if self.text:
            result['text'] = str(self.text)
        if self.value:
            result['value'] = str(self.value)
        return result

@dataclass
class Element:
    display_name: Optional[str] = None
    name: Optional[str] = None
    placeholder: Optional[str] = None
    type: Optional[str] = None
    optional: bool = True
    default: Optional[str] = None
    help_text: Optional[str] = None
    options: Optional[List[Option]] = None

    def asdict(self):
        result = {}
        if self.display_name:
            result['display_name'] = str(self.display_name)
        if self.name:
            result['name'] = str(self.name)
        if self.placeholder:
            result['placeholder'] = str(self.placeholder)
        if self.type:
            result['type'] = str(self.type)
        if self.optional:
            result['optional'] = bool(self.optional)
        if self.default:
            result['default'] = str(self.default)
        if self.help_text:
            result['help_text'] = str(self.help_text)
        if self.options:
            result['options'] = [option.asdict() for option in self.options]

        return result

@dataclass
class Dialog:
    trigger_id: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    elements: Optional[List[Element]] = None

    def asdict(self):
        result = {}
        if self.trigger_id:
            result['trigger_id'] = str(self.trigger_id)
        if self.url:
            result['url'] = str(self.url)
        if self.title:
            result['dialog'] = {
                "title": str(self.title),
                "elements": [element.asdict() for element in self.elements]
            }

        return result