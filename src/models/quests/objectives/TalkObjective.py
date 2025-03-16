from src.models.quests.QuestObjective import QuestObjective

class TalkObjective(QuestObjective):
    """Цель квеста: поговорить с определенным NPC"""
    
    def __init__(self, npc_id, description=None):
        super().__init__(QuestObjective.TYPE_TALK, description or f"Поговорить с {npc_id}")
        self.npc_id = npc_id
        self.talked = False
    
    def update_progress(self, player, game):
        """Обновляет прогресс разговора с NPC"""
        # Эта функция обычно вызывается не автоматически, а в момент разговора с NPC
        return False
    
    def mark_talked(self):
        """Отмечает, что игрок поговорил с NPC"""
        if not self.completed:
            self.talked = True
            self.completed = True
            return True
        return False
    
    def get_progress_text(self, game=None):
        """Возвращает текст с описанием прогресса разговора с NPC"""
        # Пытаемся получить имя NPC для более понятного отображения
        npc_name = self.npc_id
        
        if game is not None:
            try:
                npc = game.get_npc(self.npc_id)
                if npc is not None and hasattr(npc, 'name'):
                    npc_name = npc.name
            except Exception:
                pass
        
        status = "✅" if self.completed else "❌"
        return f"{status} Поговорить с {npc_name}" 