from .const import MODE_RECHARGE, MODE_ECO, MODE_NORMAL, OFFSET_ECO, OFFSET_CONSO_ONDULEUR
from .core import Context
import logging

_LOGGER = logging.getLogger(__name__)

class Inverter:

    name: str
    max_power: float
    solar: float
    soc: float
    soc_min: float
    soc_max: float
    consigne: float

    def __init__(self, name: str, max_power: float):
        self.name = name
        self.max_power = max_power
        self.solar = 0.0
        self.soc = 0.0
        self.soc_min = 0.0
        self.soc_max = 100.0
        self.consigne = 0

    def set(self, solar, soc, soc_min, soc_max):
        self.solar = solar
        self.soc = soc
        self.soc_min = soc_min
        self.soc_max = soc_max

    def __repr__(self):
        return (
            f"Inverter {self.name}: "
            f"solar={self.solar} - soc={self.soc} - consigne={self.consigne}"
        )

    # Permet d'indiquer si la batterie associée à l'onduleur est pleine
    def is_full(self)->bool:
        if self.soc >= self.soc_max : return True
        return False

    # Permet d'indiquer si la batterie associée à l'onduleur est vide
    def is_empty(self)->bool:
        if self.soc <= self.soc_min: return True
        return False

    # Méthode permettant de mettre à jour la consigne de l'onduleur
    def update_consigne(self, context: Context):

        _LOGGER.info(
            "INV %s | soc=%s soc_min=%s empty=%s",
            self.name,
            self.soc,
            self.soc_min,
            self.is_empty(),
        )

        consigne_brut = 0
        if context.mode == MODE_RECHARGE:
            consigne_brut =  self.consigne_mode_recharge()
        elif context.mode == MODE_ECO:
            consigne_brut = self.consigne_mode_eco(context)
        elif context.mode == MODE_NORMAL:
            consigne_brut = self.consigne_mode_normal(context)

        # Limitation de la consigne à la puissance maximal de l'onduleur
        self.consigne = int(min(consigne_brut, self.max_power))

    def consigne_mode_recharge(self)->float:
        # ####################################################################
        # En mode RECHARGE, Tout le solaire va dans la batterie
        ######################################################################
        _LOGGER.info("INV %s | RECHARGE",self.name,)
        return 0

    def consigne_mode_eco(self, context: Context)->float:
        # ####################################################################
        # En mode ECO, Priorité à la consommation provenant du solaire
        # Pas d'utilisation de la batterie
        # Si la batterie est pleine, renvoyer tout le solaire dans la maison
        # Si la voiture électrique charge, le solaire est utilisé
        ######################################################################
        _LOGGER.info("INV %s | ECO",self.name,)
        if self.is_full():
            return max(self.solar - OFFSET_ECO, 0)

        # le solaire géré total est supérieur à la charge de la maison (voiture comprise)
        if context.solar_total_managed >= context.power_consumption_total_managed:
            # On répartit proportionnellement selon le solaire de chaque onduleur
            # Le reste est automatiquement mis dans la batterie
            if context.solar_total_managed > 0:
                ratio = self.solar / context.solar_total_managed
                return max (context.power_consumption_total_managed * ratio - OFFSET_ECO, 0)
            else:
                return 0

        # Le solaire n'est pas suffisant pour couvrir la consommation de l'onduleur
        if self.solar < OFFSET_CONSO_ONDULEUR:
            return 0

        return max(self.solar - OFFSET_ECO, 0)

    def consigne_mode_normal(self, context: Context)->float:
        # ####################################################################
        # En mode NORMAL, l'onduleur utilise toute la charge solaire en priorité
        # il compense ensuite en puisant dans les batteries
        # Le solaire permet de compenser la charge total de la consommation
        # La batterie ne compense pas la charge de la voiture électrique
        ######################################################################
        _LOGGER.info("INV %s | NORMAL",self.name,)

        # le total solaire est supérieur à la charge de la maison (voiture comprise)
        if context.solar_total >= context.power_consumption_total and context.solar_total > 0:
            if self.is_full(): return max(self.solar - OFFSET_ECO, 0)
            else:
                base = context.power_consumption_total_managed * (self.solar / context.solar_total_managed)
                return max(base - OFFSET_ECO, 0)

        # Il n'y a pas assez de solaire pour compenser la charge de la maison
        # On utilise la batterie si elle n'est pas vide pour compenser la charge restante (mais pas la voiture)
        solar_unmanaged = 0
        if self.is_full(): solar_unmanaged = max(self.solar, 0)
        solar_managed = self.solar - solar_unmanaged

        nb_batteries_disponibles = context.battery_ok
        deficit = context.power_consumption_house_managed - context.solar_total_managed

        if (deficit <= 0):
            # Il y a assez de solaire pour la maison sans compter la voiture (pas besoin de batterie).
            # Essayer de donner tout le solaire possible pour la voiture
            return max(self.solar - OFFSET_ECO, 0)

        if (deficit > 0 and nb_batteries_disponibles > 0 and not self.is_empty()):
            # Il n'y a pas assez de solaire pour la maison (et donc pas non plus pour la voiture)
            if self.is_full(): return max(self.solar - OFFSET_ECO + (context.power_consumption_house_managed - context.solar_total_managed)/nb_batteries_disponibles, 0)
            else:              return max(solar_managed - OFFSET_ECO + (context.power_consumption_house_managed - context.solar_total_managed)/nb_batteries_disponibles, 0)

        # Batterie vide ou pas de batterie disponible
        return max(self.solar - OFFSET_ECO, 0)