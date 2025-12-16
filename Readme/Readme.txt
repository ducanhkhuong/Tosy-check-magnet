I.how to build and deloy
    step 1 : ./build.sh
    step 2 : 
        + sudo -i
        + cd /etc/systemd/system
        + cp /home/rpi/python_ws/HallArrayViewer/Service/hall_array_viewer.service .
        + systemctl daemon-reload
        + systemctl enable hall_array_viewer.service
    step 3 : ./update_application.sh
    done

II.how to run test
    ./home/rpi/python_ws/HallArrayViewer/bin/hall_array_viewer
    done

III.how to update system
    downloads folder UpdateSystem to other rpi 
    step 1: mkdir /home/rpi/Application/app
    step 2: mkdir /home/rpi/Application/log
    step 3: cp UpdateSystem/hall_array_viewer /home/rpi/Application/app/hall_array_viewer
    step 4: cp UpdateSystem/hall_array_viewer.log /home/rpi/Application/log/hall_array_viewer.log
    step 5: sudo -i
    step 6: 
        + cd /etc/systemd/system
        + cp UpdateSystem/hall_array_viewer.service .
        + systemctl daemon-reload
        + systemctl enable hall_array_viewer.service
        + systemctl start hall_array_viewer.service
    done