import unidecode


class Student:

    def __init__(self, full_name: str, name_from_file: str, packet_name: str, pt_percentage: float) -> None:
        self.full_name = full_name
        self.email = ""
        self.name_from_file = name_from_file.lower()
        self.packet_name = packet_name.lower()
        self.pt_percentage = pt_percentage

    def check_name_correctness(self) -> bool:
        name_wo_accents = unidecode.unidecode(self.full_name.lower())
        name_wo_accents_reversed = self.__reverse_name(name_wo_accents)
        return (name_wo_accents == self.packet_name) or (name_wo_accents_reversed == self.packet_name)

    @staticmethod
    def __reverse_name(name: str) -> str:
        words = name.split(' ')
        reversed_name = ' '.join(reversed(words))
        return reversed_name
