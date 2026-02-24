#!/bin/bash

SERVICE_NAME="hall_array_viewer.service"
FILE_EXE="$HOME/python_ws/HallArrayViewer/bin/hall_array_viewer"
DESTINATION_APP="$HOME/Application/app/hall_array_viewer"
DESTINATION_DESKTOP="$HOME/Desktop/hall_array_viewer"

echo "1.Stop service $SERVICE_NAME"
sudo systemctl stop $SERVICE_NAME

if [ ! -d "$HOME/Application" ]; then
    echo "Create $HOME/Application/app"
    mkdir -p "$HOME/Application/app"
fi

echo "copy from $FILE_EXE ----> $DESTINATION_APP"
echo "copy from $FILE_EXE ----> $DESTINATION_DESKTOP"
cp "$FILE_EXE" "$DESTINATION_APP"
cp "$FILE_EXE" "$DESTINATION_DESKTOP"

echo "2.Starting service $SERVICE_NAME..."
sudo systemctl start $SERVICE_NAME
 
echo "3.Update application done"
