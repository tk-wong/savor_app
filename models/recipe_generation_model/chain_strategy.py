import abc
from abc import ABC


class ChainStrategy(ABC):

    @abc.abstractmethod
    def build_chain(self, llm, request_runnable):
        pass

    @abc.abstractmethod
    def request_type(self):
        pass