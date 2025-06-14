import psutil
import os
import platform
import subprocess
from datetime import datetime, timedelta
import locale

# Setzt die Sprache auf Deutsch
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

logo = '''
                                    ..:-=+*******+=-:.                    
                                .:-+*%%@@@@@@@@@@@@@@@%#*=:.               
                             .-+#@@@@@@@@%%#######%@@@@@@@@%+:             
                          .-*%@@@@%#*+==--===---:....:=*#@@@@@*-.          
                       .-+%@@@%*=-----====++*#%@@@%#*=:  .=#@@@@#-         
                     .=#@@@#+:......          ..:=#@@@@@%+:  :+@@@@*.    
                .  :+%@@%+:.                      .=%@@@@@#-  .*@@@#.      
                 .+@@@#-.                       .. .-#@@@@@@*.  -@@@#.     
            .  .=%@@#-                      .:=**. .-=#@%@@@@%:  -@@@+     
             .:*@@%+.                    .-+*%@@:   .#*@@%@@@@%:  =@@%.    
           .:=%@%#:                  .:=*##%@@@-     =@%@%%@@@@#.  #@@-    
          .-+@@%*.                .-+%@%##@@@@@+.    :@@@@@#@@@@@= -@@=    
         :=+@@#+.             .:=*@@@#+#@@@@@*.      :@@@@@@#@@@@%. .@@    
        :+=@@#+.           .-+#@@@%+=#@@@@@@#.       -@@@@@@#@@@@#. .%@    
       :#:%@#+.        .:=*@@@@@#==#@@@@@@@@:      . *@@@@@*@@@@@. .%%.    
      .#-+@@+:      .-*%@@@@@%*-=#@@@@@@@@@-        :@@@@@@*@@@@%. .@=     
      *#.@@*: ...:=*%%#*+=-:...#@@@@@@@@@@+         *@@@@@%#@@@@#  =#.     
     :@--@@=...:-=-:..        .=@@@@@@@@@*.      . -@@@@@@*@@@@@= .*:      
     *@.-@@: ...               .*@@@@@@@#.        :@@@@@@@*@@@@%. --       
    .@@.-@@:                    .%@@@@@@:        :%@@@@@@#%@@@@- .:        
    :@@=.@@= .                   -@@@@@-        -@@@@@@@%#@@@@*.              
    -@@%..*@%:                    .#@*.      .=#@@@@@@@@%#@@@@=.             
    -%@@*. =@@+.                   :#.    .=#@@@@@@@@%#@@@@*.              
    -#@@@#: .+%%+:.                    .-*%@@@@@@@@@%%@@@@=.                
    -%*@@@@+. .-*#*+-:.....         .-*%@@@@@@@@@@@%@@@#:                 
    :%@*%@@@@*=:  .::-::..    ..:=+#@@@@@@@@@@@@@@%@@@%=.                  
     +@@**%@@@@@%#+==-----=+*#%@@@@@@@@@@@@@@@@@@@@@%+.                    
     .#@@%**#%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%=.                      
      .#@@@@%#**####%%%%%%%%%@@@@@@@@@@@@@@@@@@@*-.                        
       .+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#=:                           
         :*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#+-.                              
           .=#%@@@@@@@@@@@@@@@@@@@%%#+=:.                                  
              .-=*#%@@@@@@%%#*+-::.   

'''

def get_system_info():
    mem = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    uptime_seconds = int(datetime.now().timestamp() - psutil.boot_time())
    uptime_str = str(timedelta(seconds=uptime_seconds))[:-3]  

    battery_status = "Keine Batterie erkannt"
    if battery:
        if battery.power_plugged:
            battery_status = f"{battery.percent:.1f}% (am Netz)"
        else:
            remaining_time = f"{battery.secsleft // 60} Min" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unbekannt"
            battery_status = f"{battery.percent:.1f}% (es verbleiben noch {remaining_time})"

    def get_cpu_info():
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpu_info = f.read()
            
            cpu_model = None
            cpu_cores = 0
            min_freq = float('inf')
            max_freq = 0
            current_freq = 0

            for line in cpu_info.split("\n"):
                if line.startswith("model name"):
                    cpu_model = line.split(":")[1].strip()
                if line.startswith("processor"):
                    cpu_cores += 1
                if line.startswith("cpu MHz"):
                    freq = float(line.split(":")[1].strip())
                    min_freq = min(min_freq, freq)
                    max_freq = max(max_freq, freq)
                    current_freq = freq  # Aktuelle Frequenz

            return cpu_model, cpu_cores, min_freq, max_freq, current_freq
        except FileNotFoundError:
            return "Prozessor-Informationen konnten nicht gefunden werden.", 0, 0, 0, 0

    cpu_model, cpu_cores, min_freq, max_freq, current_freq = get_cpu_info()

    def get_gpu_info():
        gpu_model = "Unbekannt"
        try:
            result = subprocess.check_output("lspci", shell=True, stderr=subprocess.STDOUT).decode()
            for line in result.splitlines():
                if "VGA" in line or "3D controller" in line:
                    gpu_model = line.split(":")[2].strip()
                    break
        except subprocess.CalledProcessError:
            pass
        return gpu_model

    gpu_model = get_gpu_info()

    def get_network_info():
        wlan_model = "Unbekannt"
        lan_model = "Unbekannt"
        
        try:
            result = subprocess.check_output("lspci", shell=True, stderr=subprocess.STDOUT).decode()
            for line in result.splitlines():
                if "Network" in line and "wireless" in line.lower():
                    wlan_model = line.split(":")[2].strip()
                if "Ethernet" in line:
                    lan_model = line.split(":")[2].strip()

        except subprocess.CalledProcessError:
            pass
        
        return wlan_model, lan_model

    wlan_model, lan_model = get_network_info()

    def get_desktop_version():
        try:
            result = subprocess.check_output("cinnamon --version", shell=True, stderr=subprocess.DEVNULL).decode().strip()
            return result if result else "Nicht verfügbar"
        except subprocess.CalledProcessError:
            return "Nicht verfügbar"

    desktop_version = get_desktop_version()

    # Hintergrundbild und dessen Informationen abrufen
    def get_background_info():
        try:
            # Hier wird der Befehl für Cinnamon verwendet
            result = subprocess.check_output("gsettings get org.cinnamon.desktop.background picture-uri", shell=True, stderr=subprocess.STDOUT).decode().strip()
            # Extrahiere den Dateinamen
            image_file = result.split('/')[-1].replace('file://', '')
            return image_file
        except subprocess.CalledProcessError:
            return "Nicht verfügbar"

    background_info = get_background_info()

    # Bildschirmauflösung abrufen
    def get_resolution():
        try:
            result = subprocess.check_output("xrandr | grep '*' | uniq", shell=True, stderr=subprocess.STDOUT).decode()
            return result.strip().split()[0]  # Gibt die aktuelle Auflösung zurück
        except subprocess.CalledProcessError:
            return "Nicht verfügbar"

    resolution = get_resolution()

    # Netzwerk-Upload und Download in MB/GB anzeigen
    def get_network_speed():
        net_io = psutil.net_io_counters()
        upload = net_io.bytes_sent
        download = net_io.bytes_recv

        # Umrechnung von Bytes in MB bzw. GB
        upload_mb = upload / (1024 ** 2)
        download_mb = download / (1024 ** 2)

        if upload_mb > 1024:
            upload = upload_mb / 1024
            upload_str = f"{upload:.2f} GB"
        else:
            upload_str = f"{upload_mb:.2f} MB"

        if download_mb > 1024:
            download = download_mb / 1024
            download_str = f"{download:.2f} GB"
        else:
            download_str = f"{download_mb:.2f} MB"

        return upload_str, download_str

    upload_str, download_str = get_network_speed()

    # Gesamtgröße der Festplatte in GB von allen Partitionen
    total_disk_space = sum(psutil.disk_usage(partition.mountpoint).total for partition in psutil.disk_partitions(all=False))

    # Festplattenserie und Hersteller abrufen
    def get_disk_info():
        try:
            result = subprocess.check_output("lsblk -o SERIAL,VENDOR", shell=True, stderr=subprocess.STDOUT).decode()
            lines = result.strip().splitlines()[1:]  # Erste Zeile ist die Kopfzeile
            disk_info = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    disk_info.append(f"{parts[1]} (Serie: {parts[0]})")  # Hersteller und Serie
            return ", ".join(disk_info) if disk_info else "Nicht verfügbar"  # Kompakte Ausgabe
        except subprocess.CalledProcessError:
            return "Nicht verfügbar"

    disk_info = get_disk_info()

    return {
        "Datum und Uhrzeit": datetime.now().strftime("%A %e. %B %Y | %H:%M"),
        "Benutzer": os.getenv("USER", "Unbekannt"),
        "Betriebssystem": 'GuideOS (http://www.guideos.de)',  # Aktiver Link als Text
        "Kernel": platform.version(),
        "Architektur": platform.machine(),
        "Prozessor": f"{cpu_model} ({cpu_cores} Kerne)",
        "Maximale Taktfrequenz": f"{max_freq:.2f} MHz",
        "Minimale Taktfrequenz": f"{min_freq:.2f} MHz",
        "Aktuelle Taktfrequenz": f"{current_freq:.2f} MHz",
        "Grafikkarte": gpu_model,
        "CPU-Auslastung": f"{psutil.cpu_percent(interval=1)}%",
        "Verbauter RAM": f"{mem.total // (1024**3)} GB",
        "Genutzter RAM": f"{mem.used // (1024**3)} GB ({mem.percent}%)",
        "Festplatten Serie/Hersteller": disk_info.strip(),  # Hersteller und Serie der Festplatte
        "Verbauter Festplattenspeicher": f"{total_disk_space // (1024**3)} GB",  # Gesamtgröße der Festplatte
        "Festplatte /": f"{psutil.disk_usage('/').used // (1024**3)} GB genutzt von {total_disk_space // (1024**3)} GB",
        "Festplatte /home": f"{psutil.disk_usage('/home').used // (1024**3)} GB genutzt von {psutil.disk_usage('/home').total // (1024**3)} GB",
        "Auflösung": resolution,  # Aktuelle Bildschirmauflösung
        "Hintergrund": background_info,  # Hintergrundbildname
        "Vergangene Zeit seit Systemstart": uptime_str,
        "Batteriestand": battery_status,
        "Desktop": os.getenv("XDG_CURRENT_DESKTOP", "Unbekannt"),
        "Desktop-Version": desktop_version,
        "Icon": "Yaru",
        "Theme": "Adwaita",
        "Upload": upload_str,
        "Download": download_str,
        "Wlan-Karte": wlan_model,
        "Lan-Karte": lan_model
    }

def print_system_info():
    info = get_system_info()

    print(f"\033[1;36m{logo}\033[0m")
    print(f"\033[1;36m{info['Datum und Uhrzeit']}\033[0m")  # Blauton für die Uhrzeit
    print(f"\033[1;36mBenutzer:\033[0m {info['Benutzer']}")
    print(f"\033[1;36mBetriebssystem:\033[0m {info['Betriebssystem']}")
    print(f"\033[1;36mKernel:\033[0m {info['Kernel']}")
    print(f"\033[1;36mArchitektur:\033[0m {info['Architektur']}")
    print(f"\033[1;36mProzessor:\033[0m {info['Prozessor']}")
    print(f"\033[1;36mCPU-Auslastung:\033[0m {info['CPU-Auslastung']}")
    print(f"\033[1;36mMaximale Taktfrequenz:\033[0m {info['Maximale Taktfrequenz']}")
    print(f"\033[1;36mMinimale Taktfrequenz:\033[0m {info['Minimale Taktfrequenz']}")
    print(f"\033[1;36mAktuelle Taktfrequenz:\033[0m {info['Aktuelle Taktfrequenz']}")
    print(f"\033[1;36mGrafikkarte:\033[0m {info['Grafikkarte']}")
    print(f"\033[1;36mVerbauter RAM:\033[0m {info['Verbauter RAM']}")
    print(f"\033[1;36mGenutzter RAM:\033[0m {info['Genutzter RAM']}")
    print(f"\033[1;36mFestplatten Serie/Hersteller:\033[0m {info['Festplatten Serie/Hersteller']}")  # Hersteller und Serie
    print(f"\033[1;36mVerbauter Festplattenspeicher:\033[0m {info['Verbauter Festplattenspeicher']}")  # Geänderter Text
    print(f"\033[1;36mFestplatte /:\033[0m {info['Festplatte /']}")
    print(f"\033[1;36mFestplatte /home:\033[0m {info['Festplatte /home']}")
    print(f"\033[1;36mAuflösung:\033[0m {info['Auflösung']}")  # Aktuelle Bildschirmauflösung
    print(f"\033[1;36mHintergrund:\033[0m {info['Hintergrund']}")  # Hintergrundbildname
    print(f"\033[1;36mVergangene Zeit seit Systemstart:\033[0m {info['Vergangene Zeit seit Systemstart']}")
    print(f"\033[1;36mBatteriestand:\033[0m {info['Batteriestand']}")
    print(f"\033[1;36mDesktop:\033[0m {info['Desktop']}")
    print(f"\033[1;36mDesktop-Version:\033[0m {info['Desktop-Version']}")
    print(f"\033[1;36mIcon:\033[0m {info['Icon']}")
    print(f"\033[1;36mTheme:\033[0m {info['Theme']}")
    print(f"\033[1;36mUpload:\033[0m {info['Upload']}")
    print(f"\033[1;36mDownload:\033[0m {info['Download']}")
    print(f"\033[1;36mWlan-Karte:\033[0m {info['Wlan-Karte']}")
    print(f"\033[1;36mLan-Karte:\033[0m {info['Lan-Karte']}")

# Systeminformationen anzeigen
print_system_info()
