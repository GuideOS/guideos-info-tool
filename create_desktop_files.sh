#!/bin/bash

# Sicherstellen, dass die Verzeichnisse existieren
mkdir -p debian/guideos-info-tool/usr/share/applications
#mkdir -p debian/guideos-ticket-tool/etc/xdg/autostart

# Erstellen der ersten .desktop-Datei
cat > debian/guideos-info-tool/usr/share/applications/guideos-info-tool.desktop <<EOL
[Desktop Entry]
Version=1.0
Name=GuideOS Info Tool
Comment=Information and management tool for GuideOS
Name[de]=GuideOS Info Tool
Comment[de]=Informationstool für GuideOS
Exec=xterm -hold -geometry 125x70 -fa 'Monospace' -fs 9.0 -e guideos-info-tool
Icon=guideos-info-tool
Terminal=true
Type=Application
Categories=GuideOS;
StartupNotify=true
EOL