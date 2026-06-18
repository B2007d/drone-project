import time

class DroneController:
    def __init__(self):
        self.is_armed = False
        self.altitude = 0 # Высота в метрах

    def arm_motors(self):
        """Безопасный запуск моторов перед взлетом"""
        print("[СИСТЕМА] Проверка датчиков...")
        time.sleep(1)
        self.is_armed = True
        print("[МОТОРЫ] Моторы запущены и готовы к взлету!")

    def take_off(self, target_altitude):
        """Взлет на заданную высоту"""
        if not self.is_armed:
            print("[ОШИБКА] Нельзя взлететь! Моторы не запущены.")
            return

        print(f"[ПОЛЕТ] Взлетаем на высоту {target_altitude} м...")
        while self.altitude < target_altitude:
            self.altitude += 1
            print(f"Текущая высота: {self.altitude} м")
            time.sleep(0.5)
        print("[ПОЛЕТ] Высота набрана. Зависание.")

    def land(self):
        """Безопасная посадка"""
        print("[ПОЛЕТ] Начинаем снижение...")
        while self.altitude > 0:
            self.altitude -= 1
            print(f"Текущая высота: {self.altitude} м")
            time.sleep(0.5)
        self.is_armed = False
        print("[МОТОРЫ] Дрон сел, моторы выключены.")

# Запуск симуляции полета
if __name__ == "__main__":
    print("--- ЗАПУСК БОРТОВОГО КОМПЬЮТЕРА ДРОНА ---")
    drone = DroneController()
    
    # Логика миссии
    drone.arm_motors()
    drone.take_off(target_altitude=3)
    time.sleep(2) # Летим 2 секунды
    drone.land()
