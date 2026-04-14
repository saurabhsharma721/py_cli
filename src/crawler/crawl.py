from abc import ABC, abstractmethod

from src.entity.scrapped_link import ScrappedLink


class Crawl(ABC):
    @abstractmethod
    def crawl(self) -> list[ScrappedLink]:
        pass
