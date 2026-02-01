import logging
_LOGGER = logging.getLogger(__name__)

class Context:
    mode: str
    inverters:[]
    power_consumption_total: float
    power_consumption_total_managed: float
    power_consumption_car: float
    power_consumption_house: float
    power_consumption_house_managed: float
    solar_total: float
    solar_total_managed: float
    battery_ok: int

    def __init__(self, mode, power_consumption_total, power_consumption_car, inverters):
        self.mode = mode
        self.inverters = inverters
        self.power_consumption_total = power_consumption_total
        self.power_consumption_car = power_consumption_car
        self.solar_total = 0
        self.solar_total_managed = 0
        self.power_consumption_house = 0
        self.power_consumption_house_managed = 0
        self.power_consumption_total_managed = 0
        self.battery_ok = 0

        self.update_context()

    def update_context(self):
        self.solar_total = sum(max(inverter.solar,0) for inverter in self.inverters)
        self.power_consumption_house = max(self.power_consumption_total-self.power_consumption_car, 0)
        self.power_consumption_house_managed = max(self.power_consumption_house - self.get_power_not_managed(), 0)
        self.power_consumption_total_managed = max(self.power_consumption_total - self.get_power_not_managed(), 0)
        self.solar_total_managed = self.get_solar_managed()
        self.battery_ok = self.get_number_of_batteries_ok()

    def get_number_of_batteries_ok(self)->int:
        battery_ok = 0
        for inverter in self.inverters:
            if not inverter.is_empty():
                battery_ok = battery_ok +1
        return battery_ok

    def get_solar_managed(self)->float:
        solar_managed = self.solar_total
        for inverter in self.inverters:
            if inverter.is_full():
                solar_managed = solar_managed - inverter.solar
        return max(solar_managed, 0)



    def get_power_not_managed(self)->float:
        power_not_managed = 0
        for inverter in self.inverters:
            if inverter.is_full():
                power_not_managed = power_not_managed + inverter.solar
        return max(power_not_managed,0)


    def __repr__(self):
        return (
            f"Context: Mode={self.mode}"
            f", power_consumption_total={self.power_consumption_total}"
            f", power_consumption_house={self.power_consumption_house}"
            f", power_consumtion_house_managed={self.power_consumption_house_managed}"
            f", power_consumption_car={self.power_consumption_car}"
            f", solar={self.solar_total}\n"
            f"{self.inverters}"
        )

class Engine:

    context:Context


    def __init__(self,mode, power_consumption_total, power_consumption_car, inverters):


        self.context = Context(
            mode,
            power_consumption_total,
            power_consumption_car,
            inverters
        )

    def __repr__(self):
        return (
            f"{self.context}"
        )



    def update(self):

        _LOGGER.info(
            "ENGINE | BEFORE | mode=%r | conso_total=%.1f | solar_total=%.1f",
            self.context.mode,
            self.context.power_consumption_total,
            self.context.solar_total,
        )

        self.context.update_context()

        for inverter in self.context.inverters:
            inverter.update_consigne(self.context)


        _LOGGER.info(
            "ENGINE | AFTER  | mode=%r | solar_managed=%.1f | batteries_ok=%d",
            self.context.mode,
            self.context.solar_total_managed,
            self.context.battery_ok,
        )

        print(self.__repr__())