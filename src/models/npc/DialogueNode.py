class DialogueNode:
    """Класс для представления узла в диалоговом дереве"""
    
    def __init__(self, text, options=None, actions=None):
        self.text = text  # Текст диалога
        self.options = options or []  # Варианты ответов [{text: "", next_id: "", action: ""}]
        self.actions = actions or []  # Действия, выполняемые при входе в диалог
        
    @staticmethod
    def from_dict(data):
        """Создает узел диалога из словаря"""
        if not data:
            return None
            
        text = data.get("text", "")
        options = data.get("options", [])
        actions = data.get("actions", [])
        
        return DialogueNode(text, options, actions) 