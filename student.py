import unidecode  # umožnuje odstránenie diakritiky z mien


class Student:
    """
    Trieda študent reprezentuje jedného študenta, údaje o 
    ňom spolu s výsledkom z aktivity
    """

    def __init__(self, full_name: str, name_from_file: str, packet_name: str, pt_percentage: float) -> None:
        self.full_name = full_name
        self.email = ""
        self.name_from_file = name_from_file.lower()
        self.packet_name = packet_name.lower()
        self.pt_percentage = pt_percentage
        self.compulsory = False

    def check_name_correctness(self) -> bool:
        """kontrola, či sa meno študenta zhoduje s menom, ktoré uviedol v aktivite"""
        name_wo_accents = unidecode.unidecode(self.full_name.lower())
        name_wo_accents_reversed = self.__reverse_name(name_wo_accents)
        return name_wo_accents == self.packet_name or name_wo_accents_reversed == self.packet_name

    def email_found(self) -> bool:
        return self.email != ""

    @staticmethod
    def __reverse_name(name: str) -> str:
        """obrátenie mena, pre prípad, že ho študent uvedie ako Meno_Priezvisko"""
        words = name.split(' ')
        reversed_name = ' '.join(reversed(words))
        return reversed_name
