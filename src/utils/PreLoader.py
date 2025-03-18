from src.loaders.ItemsLoader import ItemsLoader
from src.loaders.SimpleLoader import SimpleLoader
from src.utils.Logger import Logger

class PreLoader:
    def __init__(self):
        self.logger = Logger()
        self.loaders = []
        self.ATLAS = {
            "ITEMS": ItemsLoader(),
        }
        
        # Автоматически регистрируем все загрузчики из ATLAS
        for key, loader in self.ATLAS.items():
            self.register_loader(loader)

    def register_loader(self, loader: SimpleLoader):
        self.loaders.append(loader)

    def load(self):
        """Запуск загрузки всех данных"""
        self.logger.info("PreLoader: начало загрузки данных...")
        
        # Загружаем все данные через загрузчики
        for loader in self.loaders:
            loader.load()
        
        self.logger.info("PreLoader: все данные успешно загружены")

    def get_atlas(self):
        return self.ATLAS
