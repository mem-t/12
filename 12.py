# -*- coding: utf-8 -*-

"""
ВАЖНОЕ ПРИМЕЧАНИЕ ДЛЯ ПОЛЬЗОВАТЕЛЯ:

Этот скрипт предназначен для работы в консольной среде, например, в Termux.
Он использует библиотеку pywifi для сканирования Wi-Fi сетей.

1. Особенности работы pywifi в Termux:
   Функциональность pywifi для работы с Wi-Fi в Termux может быть нестабильной
   или ограниченной из-за особенностей операционной системы Android и ее
   механизмов управления Wi-Fi. В зависимости от версии Android и настроек
   устройства, для сканирования или других операций с Wi-Fi могут потребоваться:
   - Ручное предоставление приложению Termux необходимых разрешений на доступ
     к местоположению и Wi-Fi.
   - Использование Termux-специфичных утилит или API (например, Termux:API и
     termux-wifi-info, termux-wifi-scaninfo), которые могут быть более
     совместимы с Android, чем стандартные Python библиотеки.
   - На некоторых устройствах или для определенных действий может потребоваться
     наличие root-прав.
   Если скрипт сталкивается с ошибками при сканировании Wi-Fi, это,
   вероятно, связано с ограничениями доступа к аппаратной части Wi-Fi в Termux
   без дополнительных настроек или разрешений.

2. Этическое использование:
   Данный скрипт является инструментом для анализа сетевой активности. Он
   может быть использован для обнаружения и анализа открытых Wi-Fi сетей
   или сетей с определенными характеристиками ("Evil Portal").
   Используйте этот скрипт ответственно и исключительно в сетях, на
   тестирование которых у вас есть явное разрешение.
   Любое несанкционированное сканирование или взаимодействие с чужими сетями
   может нарушать законодательство вашей страны. Автор скрипта не несет
   ответственности за неправомерное использование данного инструмента.

3. Остановка скрипта:
   Для остановки выполнения скрипта в консоли обычно используется сочетание
   клавиш Ctrl+C.
"""

import os
import subprocess
import sys
import time
import threading
from datetime import datetime

# --- Проверка и установка необходимых модулей ---
def check_and_install_package(package_name):
    """
    Проверяет наличие модуля и устанавливает его, если он отсутствует.
    """
    try:
        __import__(package_name)
        # add_log заменяет GUI-текстбокс, поэтому используем print до ее определения/инициализации
        print(f"Модуль '{package_name}' уже установлен.")
        return True
    except ImportError:
        print(f"Модуль '{package_name}' не найден. Попытка установки...")
        try:
            # Используем sys.executable для запуска pip, связанного с текущим Python
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"Модуль '{package_name}' успешно установлен.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при установке модуля '{package_name}': {e}")
            print("Пожалуйста, установите его вручную, выполнив:")
            print(f"pip install {package_name}")
            return False
        except Exception as e:
             print(f"Неожиданная ошибка при установке '{package_name}': {e}")
             print("Пожалуйста, установите его вручную, выполнив:")
             print(f"pip install {package_name}")
             return False

# Проверяем и устанавливаем зависимости, нужные для консольной версии
# Удалены customtkinter и tkinter
required_packages = ['pywifi', 'requests', 'setuptools']
print("Проверка и установка необходимых зависимостей...")
for package in required_packages:
    if not check_and_install_package(package):
        print(f"Не удалось установить все необходимые модули. Скрипт может работать некорректно без модуля '{package}'.")
        # В консольной версии можно продолжить, но с предупреждением, или жестко выйти
        # sys.exit(1) # Можно раскомментировать для жесткого выхода при ошибке установки

# Теперь, когда зависимости проверены/установлены, можно безопасно импортировать
try:
    import pywifi
    from pywifi import const # Используется для статусов соединения
except ImportError:
    print("Критическая ошибка: Модуль pywifi не доступен после попытки установки. Невозможно продолжить.")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Критическая ошибка: Модуль requests не доступен после попытки установки. Невозможно продолжить.")
    sys.exit(1)

print("Все необходимые модули доступны.")

# --- Консольные функции (замена GUI-виджетов) ---

def add_log(message):
    """
    Выводит сообщение в консоль с текущей датой и временем.
    Заменяет вставку текста в GUI-текстбокс.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def clearall():
    """
    Очищает экран консоли.
    Заменяет очистку GUI-текстбокса.
    """
    # os.name == 'nt' для Windows, os.name == 'posix' для Linux/Unix/Termux
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')
    else:
        # Запасной вариант для других систем или если os.system не работает
        print("\n" * 50)
    add_log("Консоль очищена.")

# --- Основная логика сканирования (адаптирована для консоли) ---

def scan():
    """
    Функция сканирования Wi-Fi сетей и проверки на Evil Portal.
    Удалены все вызовы, связанные с GUI (обновление виджетов, интерактив).
    Теперь просто выполняет сканирование и выводит результаты в консоль.
    """
    add_log("Инициализация сканирования Wi-Fi...")
    try:
        wifi = pywifi.PyWiFi()
        ifaces = wifi.interfaces()
        if not ifaces:
            add_log("Ошибка: Wi-Fi интерфейс не найден. Убедитесь, что Wi-Fi включен и доступны необходимые разрешения.")
            # В консольной версии поток может просто завершиться или попытаться снова позже
            return # Выход из потока сканирования

        # Используем первый доступный интерфейс (как правило, wlan0 или схожий)
        iface = ifaces[0]
        add_log(f"Используется Wi-Fi интерфейс: {iface.name()}")

        # Проверка статуса интерфейса - может вести себя по-разному в Termux/Android
        try:
             iface_status = iface.status()
             if iface_status == const.IFACE_DISCONNECTED:
                 add_log(f"Интерфейс {iface.name()} находится в состоянии отключен.")
             elif iface_status == const.IFACE_CONNECTED:
                 add_log(f"Интерфейс {iface.name()} находится в состоянии подключен.")
             elif iface_status == const.IFACE_SCANNING:
                 add_log(f"Интерфейс {iface.name()} находится в состоянии сканирования.")
             else:
                  add_log(f"Интерфейс {iface.name()} в неизвестном состоянии: {iface_status}.")

        except NotImplementedError:
             add_log(f"Интерфейс {iface.name()} не полностью поддерживает проверку статуса через pywifi. Продолжаем...")
        except Exception as e:
             add_log(f"Ошибка при проверке статуса интерфейса {iface.name()}: {e}. Продолжаем...")


    except pywifi.PyWiFiError as e:
        add_log(f"Ошибка инициализации pywifi: {e}. Возможно, требуются root-права или дополнительные настройки в Termux.")
        return # Выход из потока сканирования
    except Exception as e:
        add_log(f"Неожиданная ошибка при инициализации Wi-Fi: {e}")
        return # Выход из потока сканирования


    # Основной цикл сканирования
    # Этот цикл будет работать непрерывно, пока поток не будет остановлен (например, через остановку основного скрипта)
    while True:
        add_log("Запуск сканирования сетей...")
        try:
            # Запускаем сканирование
            # В Termux это может потребовать специфических разрешений или настройки wifi-control
            iface.scan()
            # Даем время адаптеру на завершение сканирования и сбор результатов
            # Время ожидания может потребоваться настроить для вашей среды
            time.sleep(10)

            scan_results = iface.scan_results()
            add_log(f"Обнаружено {len(scan_results)} Wi-Fi сетей.")

            evil_portal_networks = []
            for network in scan_results:
                ssid = network.ssid
                bssid = network.bssid
                signal = network.signal
                # Канал и частота могут быть не всегда доступны или точны через pywifi в Termux
                channel = network.channel if hasattr(network, 'channel') else 'N/A'
                freq = network.freq if hasattr(network, 'freq') else 'N/A'

                # --- Плейсхолдер для логики определения "Evil Portal" ---
                # Эту часть необходимо адаптировать, используя реальную логику из исходного скрипта.
                # Пример: Проверка по названию SSID или типу аутентификации (если доступно)
                is_evil_portal = False
                # Например, если "Evil Portal" - это открытая сеть с определенным SSID:
                # if "Free_Public_WiFi" in ssid and network.auth == const.AUTH_ALG_OPEN:
                #    is_evil_portal = True
                # Пример очень простой placeholder-логики:
                if "Evil_" in ssid or "Free_Hotspot" in ssid or ("Guest" in ssid and signal > -70): # Просто пример
                    is_evil_portal = True
                # --- Конец плейсхолдера ---


                if is_evil_portal:
                    evil_portal_networks.append({'bssid': bssid, 'ssid': ssid, 'signal': signal, 'channel': channel, 'freq': freq})
                    add_log(f"ОБНАРУЖЕН Evil Portal: SSID='{ssid}', BSSID='{bssid}', Сигнал={signal}dBm")

            if evil_portal_networks:
                add_log(f"Обнаружено {len(evil_portal_networks)} потенциальных Evil Portal:")
                # Выводим информацию об обнаруженных сетях
                for i, network_info in enumerate(evil_portal_networks):
                    # Изменено сообщение согласно требованиям пользователя (без "атакуем")
                    add_log(f"{i+1}: SSID='{network_info['ssid']}', BSSID='{network_info['bssid']}', Сигнал={network_info['signal']}dBm - Потенциальный Evil Portal, проверка...")
                    # Здесь может быть вызов функции для дальнейшего анализа/взаимодействия
                    # Например: analyze_portal(network_info)
            else:
                add_log("Потенциальные Evil Portal не обнаружены в текущем сканировании.")

        except pywifi.PyWiFiError as e:
            add_log(f"Ошибка при выполнении сканирования pywifi: {e}. Проверьте разрешения или интерфейс Wi-Fi.")
        except requests.exceptions.RequestException as e:
             add_log(f"Ошибка HTTP запроса при проверке портала (если логика проверки Evil Portal выполняла запросы): {e}")
        except Exception as e:
            add_log(f"Неожиданная ошибка в процессе сканирования: {e}")

        # Пауза между циклами сканирования
        scan_interval_seconds = 90 # Настраиваемый интервал (например, 90 секунд)
        add_log(f"Пауза до следующего сканирования ({scan_interval_seconds} сек)...")
        time.sleep(scan_interval_seconds)


# --- Основная точка входа скрипта ---

if __name__ == "__main__":
    # Удален window = customtkinter.CTk() и все связанные с GUI вызовы
    add_log("Скрипт запущен в консольном режиме.")
    # Clearall можно вызвать для старта с чистого экрана, если нужно
    # clearall()

    # Запуск потока сканирования
    # daemon=True позволяет потоку автоматически завершиться при выходе основного скрипта
    scan_thread = threading.Thread(target=scan, daemon=True)
    scan_thread.start()
    add_log("Поток сканирования Wi-Fi запущен в фоновом режиме.")
    add_log("Нажмите Ctrl+C для остановки скрипта.")

    # Главный поток просто ожидает прерывания (Ctrl+C), поддерживая жизнь daemon потока
    try:
        # Бесконечный цикл для поддержания жизни основного потока.
        # Thread с daemon=True завершится автоматически, когда главный поток завершится.
        while True:
            # Небольшая пауза, чтобы не нагружать процессор без необходимости
            time.sleep(1)

    except KeyboardInterrupt:
        # Обработка прерывания по Ctrl+C
        add_log("\nПолучено прерывание Ctrl+C. Завершение работы скрипта...")
        # Поток сканирования (daemon=True) завершится автоматически при sys.exit()
        sys.exit(0)
    except Exception as e:
        # Обработка любых других неожиданных ошибок в основном потоке
        add_log(f"\nНеожиданная ошибка в основном потоке: {e}")
        sys.exit(1)

