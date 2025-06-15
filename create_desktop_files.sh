#!/bin/bash

# Sicherstellen, dass die Verzeichnisse existieren
mkdir -p debian/guideos-energy-tool/usr/share/applications
#mkdir -p debian/guideos-ticket-tool/etc/xdg/autostart

# Erstellen der ersten .desktop-Datei
cat > debian/guideos-energy-tool/usr/share/applications/guideos-energy-tool.desktop <<EOL
[Desktop Entry]
Version=1.0
Name=GuideOS Energy Tool
Comment=Energy management tool for GuideOS
Name[de]=GuideOS Energie Tool
Comment[de]=Energieverwaltungstool für GuideOS
Exec=guideos-energy-tool
Icon=guideos-energy-tool
Terminal=false
Type=Application
Categories=GuideOS;
StartupNotify=true
EOL