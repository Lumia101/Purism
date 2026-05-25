from abc import ABC, abstractmethod

class BaseFilter(ABC):
    @abstractmethod
    def filter(self, text: str) -> bool:
        pass