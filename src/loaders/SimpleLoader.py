from abc import ABC, abstractmethod

class SimpleLoader(ABC):
    @abstractmethod
    def load(self):
        pass