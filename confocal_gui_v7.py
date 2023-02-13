import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import bpc303
from confocal_gui_ui_v12 import Ui_MainWindow
import functions
import time
import numpy as np
import timeit
import pm100usb
from math import log10, floor

# import numpy as np

if not os.path.exists('event_log.txt'):
    with open('event_log.txt', 'w') as file:
        pass


class mywindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Class expanding the main application window designed in QtDesigner
    and exported to .py format using pyuic5"""

    def __init__(self, parent=None):
        """Create QMainWindow and connect UI elements to methods"""

        super(mywindow, self).__init__(parent)
        self.temp = None
        self.powermeter = None
        self.setupUi(self)

        self.stage = None

        self.pushButton_conn_piezos.clicked.connect(self.connectDeviceClicked)
        self.pushButton_conn_daq.clicked.connect(self.connectPowermeterClicked)
        # self.identifyDevice.clicked.connect(self.identifyDeviceClicked)
        self.pushButton_zero_x.clicked.connect(lambda: self.setZeroClicked('x'))
        self.pushButton_zero_y.clicked.connect(lambda: self.setZeroClicked('y'))
        self.pushButton_zero_z.clicked.connect(lambda: self.setZeroClicked('z'))

        self.pushButton_go_to_x_y.clicked.connect(self.setPositionXY)
        self.pushButton_go_to_z.clicked.connect(self.setPositionZ)

        self.checkBox_use_range_xy.clicked.connect(lambda: self.set_sweep_method_xy_range())
        self.checkBox_use_pixels_xy.clicked.connect(lambda: self.set_sweep_method_xy_pix())
        self.pushButton_show_fov.clicked.connect(lambda: self.show_fov())

        self.checkBox_use_range_z.clicked.connect(lambda: self.set_sweep_method_z_range())
        self.checkBox_use_pixels_z.clicked.connect(lambda: self.set_sweep_method_z_pix())
        self.pushButton_set_z_stack.clicked.connect(lambda: self.set_z_stack())

        self.pushButton_start_scan.clicked.connect(lambda: self.scan_away())
        self.pushButton_single_pixel_scan.clicked.connect(lambda: self.scan_single_pixel())

        self.pushButton_save_parameters.clicked.connect(lambda: self.save_parameters())
        self.pushButton_exit.clicked.connect(lambda: self.exit_confocal())

        self.dial_range_x.valueChanged.connect(lambda: self.x_dial_moved())
        self.dial_range_y.valueChanged.connect(lambda: self.y_dial_moved())

        self.pushButton_plot_data.clicked.connect(lambda: self.plot_data())
        self.pushButton_save_data.clicked.connect(lambda: self.save_data())

        # self.horizontalSlider_x_start.sliderChange.connect(lambda: self.x_slider_moved())
        # self.verticalSlider_y_start.sliderChange.connect(lambda: self.y_slider_moved())
        # self.dial_range_y.valueChanged.connect(lambda: self.y_dial_moved())

        """Get the parameters from last saved point."""
        params = functions.read_parameters()

        self.piezo_ID.setText(str(params["piezo_ID"]))
        self.daq_ID.setText(str(params["daq_ID"]))

        self.step_size_x_y.setText(str(params["step_size_x_y"]))
        self.center_z.setText(str(params["step_size_z"]))

        self.center_x.setText(str(params["center_x"]))
        self.center_y.setText(str(params["center_y"]))
        self.center_z.setText(str(params["center_z"]))

        self.range_x.setText(str(params["range_x"]))
        self.range_y.setText(str(params["range_y"]))
        self.range_z.setText(str(params["range_z"]))

        self.dial_range_x.setProperty("value", params["range_x"])
        self.dial_range_y.setProperty("value", params["range_y"])

        # self.dial_range_x.setProperty("value", params["range_x"])
        # self.dial_range_y.setProperty("value", params["range_y"])

        self.num_pixels_x.setText(str(params["num_pixels_x"]))
        self.num_pixels_y.setText(str(params["num_pixels_y"]))
        self.num_pixels_z.setText(str(params["num_pixels_z"]))
        self.num_frames.setText(str(params["num_frames"]))

        self.center_x_singlepix.setText(str(params["center_x_singlepix"]))
        self.center_y_singlepix.setText(str(params["center_y_singlepix"]))
        self.center_z_singlepix.setText(str(params["center_z_singlepix"]))

    def connectDeviceClicked(self):

        # print("Connect to piezos is clicked.")

        """
        Method handling clicks on the connectDevice button by:
            - checking the piezo_ID string retrieved from the piezo_ID text
                box is valid
            - populating self.stage with an instance of the BPC303 class based
                on the piezo_ID string
            - running the stage's connect() method
            - enabling other UI elements as suitable
        """
        # self.pushButton_conn_piezos.setText(text)
        # retrieve ID from text box
        ID = self.piezo_ID.text()

        # print(self.piezo_ID.value())
        if ID == "71854109":
            # create BPC303 instance
            self.stage = bpc303.BPC303(ID)
            try:
                # initialize physical instrument
                self.stage.connect()
                last_event = functions.update_event_log(f"Connection established with device: {ID}")
                self.info_box.setText(last_event)

            except:
                print('CANT CONNECT')
            try:
                # set to close loop mode
                self.stage.set_close_loop(True)
                last_event = functions.update_event_log("Piezo control mode set to closed loop")
                self.info_box.setText(last_event)

            except:
                raise
            # update connection LED
            self.pushButton_conn_piezos.setStyleSheet("background-color: green;")
            # enable UI elements
            # self.identifyDevice.setEnabled(True)
            self.pushButton_zero_x.setEnabled(True)
            self.pushButton_zero_y.setEnabled(True)
            self.pushButton_zero_z.setEnabled(True)
            self.pushButton_go_to_x_y.setEnabled(True)
            self.pushButton_go_to_z.setEnabled(True)
            # grab instrument info and update text box
            # info = self.stage.get_info()
            # self.deviceInfo.clear()
            # self.deviceInfo.appendPlainText(info)
        else:
            self.pushButton_conn_piezos.setStyleSheet("background-color: red;")
            last_event = functions.update_event_log("Piezo connection failed. Check serial number.")
            self.info_box.setText(last_event)

    def setZeroClicked(self, dimension):
        print(dimension)
        """
        Method handling clicks on the setZero button by calling the stage's
        zero method
        """
        self.stage.zero(axis=dimension)

        self.center_x.setText("0")
        self.center_y.setText("0")
        self.center_z.setText("0")

        self.center_x_singlepix.setText("0")
        self.center_y_singlepix.setText("0")
        self.center_z_singlepix.setText("0")

        last_event = functions.update_event_log(f"{dimension} motor zeroed.")
        self.info_box.setText(last_event)

    def setPositionXY(self):
        x = float(self.center_x.text())
        y = float(self.center_y.text())

        if x < 0 or y < 0:
            last_event = functions.update_event_log(f"X, Y motors cannot go to negative positions.")
            self.info_box.setText(last_event)
        elif x > 20 or y > 20:
            last_event = functions.update_event_log(f"X, Y motors cannot go to beyond 20 um.")
            self.info_box.setText(last_event)
        else:
            # TODO check if the user entered a number or a char. TypeError?

            self.stage.set_position(x=x, y=y, z=None)

            last_event = functions.update_event_log(f"X motor sent to {x} um. Y motor sent to {y} um")
            self.info_box.setText(last_event)

    def setPositionZ(self):
        z = float(self.center_z.text())
        if z < 0:
            last_event = functions.update_event_log(f"Z motor cannot go to negative positions.")
            self.info_box.setText(last_event)
        elif z > 20:
            last_event = functions.update_event_log(f"X, Y motors cannot go to beyond 20 um.")
            self.info_box.setText(last_event)
        else:
            # TODO check if the user entered a number or a char. TypeError?

            self.stage.set_position(x=None, y=None, z=z)

            last_event = functions.update_event_log(f"Z motor sent to {z} um")
            self.info_box.setText(last_event)

    def set_sweep_method_xy_pix(self):
        # self.checkBox_use_pixels_xy.setChecked(True)
        sweep_method_xy = "Pixel"
        # print(sweep_method_xy)
        self.sweep_choice.setText(sweep_method_xy)
        self.checkBox_use_range_xy.setChecked(False)

    def set_sweep_method_xy_range(self):
        # self.checkBox_use_range_xy.setChecked(True)
        sweep_method_xy = "Range"
        # print(sweep_method_xy)
        self.sweep_choice.setText(sweep_method_xy)
        self.checkBox_use_pixels_xy.setChecked(False)

    def set_sweep_method_z_pix(self):
        sweep_method_z = "Pixel"
        # print(sweep_method_z)
        self.sweep_choice_z.setText(sweep_method_z)
        self.checkBox_use_range_z.setChecked(False)

    def set_sweep_method_z_range(self):
        sweep_method_z = "Range"
        # print(sweep_method_z)
        self.sweep_choice_z.setText(sweep_method_z)
        self.checkBox_use_pixels_z.setChecked(False)

    def x_dial_moved(self):
        range_x = self.dial_range_x.value()
        self.range_x.setText(str(range_x))

    def y_dial_moved(self):
        range_y = self.dial_range_y.value()
        self.range_y.setText(str(range_y))

    # def x_slider_moved(self):
    #     x_start = self.horizontalSlider_x_start.value()
    #
    # def y_slider_moved(self):
    #     y_start = self.verticalSlider_y_start.value()

    def show_fov(self):
        step_size_x_y = float(self.step_size_x_y.text())
        center_x = float(self.center_x.text())
        center_y = float(self.center_y.text())
        # TODO check if the user entered a number or a char. TypeError?
        sweep_method_xy = self.sweep_choice.text()
        while True:
            match sweep_method_xy:
                case "Pixel":
                    # print("Pixel")
                    num_pixels_x = int(self.num_pixels_x.text())
                    num_pixels_y = int(self.num_pixels_y.text())
                    if (num_pixels_x % 2) == 1 and (num_pixels_y % 2) == 1:
                        # TODO check if pixel number is an integer
                        # TODO check if the user entered a number or a char. TypeError?
                        range_x = (num_pixels_x - 1) * step_size_x_y
                        range_y = (num_pixels_y - 1) * step_size_x_y
                        (x_start, x_end) = functions.calculate_start_end_points(center_x,
                                                                                step_size_x_y, num_pixels_x)
                        (y_start, y_end) = functions.calculate_start_end_points(center_y,
                                                                                step_size_x_y, num_pixels_y)
                        self.horizontalSlider_x_start.setProperty("value", x_start)
                        self.verticalSlider_y_start.setProperty("value", y_start)
                        print(x_start, x_end, y_start, y_end)

                        if range_x > 20 or range_y > 20:
                            last_event = functions.update_event_log(f"X, Y ranges cannot be larger than 20 um. ")
                            self.info_box.setText(last_event)
                            break
                        elif x_start < 0 or x_end > 20 or y_start < 0 or y_end > 20:
                            last_event = functions.update_event_log(f"X, Y values should be between 0 and 20.")
                            self.info_box.setText(last_event)
                            break
                        else:
                            self.range_x.setText(str(range_x))
                            self.range_y.setText(str(range_y))
                            self.dial_range_x.setProperty("value", range_x)
                            self.dial_range_y.setProperty("value", range_y)
                            dx = int(x_start / 20 * 140)
                            dy = int(y_start / 20 * 140)
                            x_dim = int(range_x / 20 * 140)
                            y_dim = int(range_y / 20 * 140)
                            self.graphicsView_chosen_FOV.setGeometry(QtCore.QRect(340 + dx, 80 + dy, x_dim, y_dim))
                            last_event = functions.update_event_log('FOV calculated.')
                            self.info_box.setText(last_event)
                            break
                    else:
                        last_event = functions.update_event_log('Pixel number should be an odd integer.')
                        self.info_box.setText(last_event)
                        break

                case "Range":
                    # print("Range")
                    range_x = float(self.range_x.text())
                    range_y = float(self.range_y.text())
                    self.dial_range_x.setProperty("value", range_x)
                    self.dial_range_y.setProperty("value", range_y)
                    num_pixels_x = range_x / step_size_x_y + 1
                    num_pixels_y = range_y / step_size_x_y + 1

                    (x_start, x_end) = functions.calculate_start_end_points(center_x,
                                                                            step_size_x_y, num_pixels_x)
                    (y_start, y_end) = functions.calculate_start_end_points(center_y,
                                                                            step_size_x_y, num_pixels_y)
                    self.horizontalSlider_x_start.setProperty("value", x_start)
                    self.verticalSlider_y_start.setProperty("value", y_start)
                    if range_x > 20 or range_y > 20:
                        last_event = functions.update_event_log(f"X, Y ranges cannot be larger than 20 um.")
                        self.info_box.setText(last_event)
                        break
                    elif x_start < 0 or x_end > 20 or y_start < 0 or y_end > 20:
                        last_event = functions.update_event_log(f"X, Y values should be between 0 and 20.")
                        self.info_box.setText(last_event)
                        break
                    else:
                        # TODO check if the user entered a number or a char. TypeError?
                        self.num_pixels_x.setText(str(num_pixels_x))
                        self.num_pixels_y.setText(str(num_pixels_y))
                        dx = int(x_start / 20 * 140)
                        dy = int(y_start / 20 * 140)
                        x_dim = int(range_x / 20 * 140)
                        y_dim = int(range_y / 20 * 140)
                        self.graphicsView_chosen_FOV.setGeometry(QtCore.QRect(340 + dx, 80 + dy, x_dim, y_dim))
                        last_event = functions.update_event_log('FOV calculated.')
                        self.info_box.setText(last_event)
                        break

                case "":
                    last_event = functions.update_event_log('No selection was made for x-y sweep type. '
                                                            'Select Pixel or Range.')
                    self.info_box.setText(last_event)
                    break

    #             TODO when i first press range then pixel if I dont
    #              change the value in the boxes the program dies

    def set_z_stack(self):
        step_size_z = float(self.step_size_z.text())
        # TODO check if the user entered a number or a char. TypeError?
        sweep_method_z = self.sweep_choice_z.text()
        center_z = float(self.center_z.text())
        match sweep_method_z:
            case "Pixel":
                # print("Pixel")
                num_pixels_z = int(self.num_pixels_z.text())
                if (num_pixels_z % 2) == 1:
                    # TODO check if the user entered a number or a char. TypeError?
                    range_z = (num_pixels_z - 1) * step_size_z
                    (z_start, z_end) = functions.calculate_start_end_points(center_z,
                                                                            step_size_z, num_pixels_z)
                    if range_z > 20:
                        last_event = functions.update_event_log(f"Z range cannot be larger than 20 um.")
                        self.info_box.setText(last_event)
                    elif z_start < 0 or z_end > 20:
                        last_event = functions.update_event_log(f"Z values should be between 0 and 20.")
                        self.info_box.setText(last_event)
                    else:
                        self.range_z.setText(str(range_z))

                        # self.num_frames.setText(str(num_pixels_z))
                else:
                    last_event = functions.update_event_log('Pixel number should be an odd integer.')
                    self.info_box.setText(last_event)

            case "Range":
                # print("Range")
                range_z = float(self.range_z.text())
                num_pixels_z = range_z / step_size_z + 1
                # TODO check if the user entered a number or a char. TypeError?
                (z_start, z_end) = functions.calculate_start_end_points(center_z,
                                                                        step_size_z, num_pixels_z)
                if range_z > 20:
                    last_event = functions.update_event_log(f"Z range cannot be larger than 20 um.")
                    self.info_box.setText(last_event)
                elif z_start < 0 or z_end > 20:
                    last_event = functions.update_event_log(f"Z values should be between 0 and 20.")
                    self.info_box.setText(last_event)
                else:
                    self.num_pixels_z.setText(str(num_pixels_z))
                    # self.num_frames.setText(str(num_pixels_z))
            case "":
                last_event = functions.update_event_log('No selection was made for z sweep type. '
                                                        'Select Pixel or Range.')
                self.info_box.setText(last_event)

    def scan_away(self):
        # TODO add checks for range, start and end points
        step_size_x_y = float(self.step_size_x_y.text())
        num_pixels_x = int(self.num_pixels_x.text())
        num_pixels_y = int(self.num_pixels_y.text())
        center_x = float(self.center_x.text())
        center_y = float(self.center_y.text())
        # TODO can pull x_start, y_slider data from the sliders instead of calling the functions
        (x_start, x_end) = functions.calculate_start_end_points(center_x,
                                                                step_size_x_y, num_pixels_x)
        (y_start, y_end) = functions.calculate_start_end_points(center_y,
                                                                step_size_x_y, num_pixels_y)
        # xs_all = np.arange(x_start, x_end, step_size_x_y)
        xs_all = np.linspace(start=x_start, stop=x_end, num=num_pixels_x, endpoint=True)
        # ys_all = np.arange(y_start, y_end, step_size_x_y)
        ys_all = np.linspace(start=y_start, stop=y_end, num=num_pixels_y, endpoint=True)
        total_pixels_in_frame = num_pixels_x * num_pixels_y
        # self.stage.set_position(x=x_start, y=None, z=None)
        # self.stage.set_position(x=None, y=y_start, z=None)


        """Things that will need to be checked before scanning:
        Number of Frames, If Z is to be scanned"""

        z_scanned = self.groupBox_2.isChecked()
        center_z = float(self.center_z.text())
        if z_scanned:
            print("z will be scanned")
            """Then z is to be scanned, we already know the pixel size, range, center."""
            step_size_z = float(self.step_size_z.text())
            num_pixels_z = int(self.num_pixels_z.text())
            # z_center = float(self.center_z.text())
            (z_start, z_end) = functions.calculate_start_end_points(center_z,
                                                                    step_size_z, num_pixels_z)
            zs_all = np.arange(z_start, z_end, step_size_z)
            print(step_size_z, z_start, z_end, zs_all)
        else:
            print("z will not be scanned")
            num_pixels_z = 1
            # self.num_pixels_z.setText(num_pixels_z)
            step_size_z = 0
            z_start = center_z
            z_end = z_start
            zs_all = z_start
            print(step_size_z, z_start, z_end, zs_all)

        num_frames = int(self.num_frames.text())
        total_frames = num_frames * num_pixels_z
        total_pixels_in_stack = total_frames * total_pixels_in_frame
        print(num_frames, total_frames, total_pixels_in_stack)

        # TODO disable all x,y,z related buttons etc while scanning then enable again
        # TODO add stop scan functionality

        if not type(zs_all) == list():
            zs_all = list([zs_all])

        frames_all = range(1, num_frames)

        if not type(frames_all) == list():
            frames_all = list([frames_all])

        self.label_finished_rows.setText(f"0 out of {num_pixels_y}")
        self.label_finished_frames.setText(f"0 out of {num_frames}")
        self.label_finished_z_steps.setText(f"0 out of {num_pixels_z}")

        rows, cols = (num_pixels_x, num_pixels_y)
        data_array = [[0 for i in range(cols)] for j in range(rows)]

        for index_z, z_value in enumerate(zs_all):
            print('scanning z')
            # z_value = zs_all[index_z]
            self.stage.set_position(x=None, y=None, z=z_value)
            time.sleep(1)

            for index_frame, frame_value in enumerate(frames_all):
                print('scanning frame')
                time.sleep(1)

                for index_y, y_value in enumerate(ys_all):
                    print('scanning y')
                    self.stage.set_position(x=None, y=y_value, z=None)
                    # time.sleep(1)

                    for index_x, x_value in enumerate(xs_all):
                        tic = timeit.default_timer()
                        # print('scanning x')
                        self.stage.set_position(x=x_value, y=None, z=None)
                        # time.sleep(1)
                        toc = timeit.default_timer()
                        print(toc - tic)

                        data_array[index_x][index_y] = self.powermeter.get_power_data()
                        time.sleep(0.001)

                    # print(index_frame+1, index_y+1, num_pixels_x, total_pixels_in_stack)
                    progress = (index_frame + 1) * (index_y + 1) * num_pixels_x / total_pixels_in_stack * 100
                    # print(progress)
                    self.progressBar_scan.setProperty("value", progress)
                    self.label_finished_rows.setText(f"{index_y + 1} out of {num_pixels_y}")

                self.label_finished_frames.setText(f"{index_frame + 1} out of {num_frames}")

            self.label_finished_z_steps.setText(f"{index_z + 1} out of {num_pixels_z}")

        last_event = functions.update_event_log('Scan finished.')
        self.info_box.setText(last_event)

        # print(data_array)
        np.savetxt('DATA_ARRAY.txt', np.array(data_array), delimiter=', ')

    def scan_single_pixel(self):
        x_singlepix = float(self.center_x_singlepix.text())
        y_singlepix = float(self.center_y_singlepix.text())
        z_singlepix = float(self.center_z_singlepix.text())

        # self.stage.set_position(x=x_singlepix, y=y_singlepix, z=z_singlepix)

        self.powermeter.set_average(10)
        print("average set")

        functions.do_every(1, self.update_power)
        self.label_single_pixel_power.setText(f"{self.temp} mW")
        # while True:
        # power = self.powermeter.get_power_data() * 1e3
        # # power = round(power, -int(floor(log10(abs(power)))))
        # power = round(power*1e3, 3)
        # self.label_single_pixel_power.setText(f"{power} mW")
        # time.sleep(0.5)

        # tic1 = timeit.default_timer()
        # print(powermeter.get_power_data() * 1e3)
        # toc1 = timeit.default_timer()
        # print(f"elapsed time: {(toc1 - tic1) * 1e3} ms")

        last_event = functions.update_event_log('Scanned single pixel.')
        self.info_box.setText(last_event)

        # while True:
        #         # TODO get data from powermeter every xx second, show it on the label, also store it?

    # def exit_confocal(self):
    #     app = QtWidgets.QApplication(sys.argv)
    #     app.aboutToQuit.connect(main.cleanup)
    #     app.aboutToQuit.connect(app.deleteLater)
    #
    #     sys.exit(app.exec_())

    def update_power(self):

        power = self.powermeter.get_power_data() * 1e3
        # power = round(power, -int(floor(log10(abs(power)))))
        power = round(power * 1e3, 3)
        self.temp = str(power)
        # self.label_single_pixel_power.setText(f"{self.temp} mW")
        time.sleep(0.2)
        print(power)
        # time.sleep(0.3)
        # return str(power)

    def connectPowermeterClicked(self):
        serial = self.daq_ID.text()
        try:
            self.powermeter = pm100usb.PM100USB(serial)
            last_event = functions.update_event_log(f"Connection established with device: {serial}")
            self.info_box.setText(last_event)
            self.pushButton_conn_daq.setStyleSheet("background-color: green;")
            self.powermeter.set_wavelength(1550)
            last_event = functions.update_event_log(f"Wavelength set to 1550 nm")
            self.info_box.setText(last_event)
        except:
            print('CANT CONNECT to powermeter')
            self.pushButton_conn_daq.setStyleSheet("background-color: red;")
            last_event = functions.update_event_log("Powermeter connection failed. Check serial number.")
            self.info_box.setText(last_event)

    def save_parameters(self):
        params = functions.read_parameters()

        params["piezo_ID"] = self.piezo_ID.text()

        params["step_size_x_y"] = float(self.step_size_x_y.text())
        params["step_size_z"] = float(self.step_size_z.text())
        print('steps done')

        params["center_x"] = float(self.center_x.text())
        params["center_y"] = float(self.center_y.text())
        params["center_z"] = float(self.center_z.text())

        params["range_x"] = float(self.range_x.text())
        params["range_y"] = float(self.range_y.text())
        params["range_z"] = float(self.range_z.text())

        params["num_pixels_x"] = int(self.num_pixels_x.text())
        params["num_pixels_y"] = int(self.num_pixels_y.text())
        params["num_pixels_z"] = int(self.num_pixels_z.text())
        params["num_frames"] = int(self.num_frames.text())

        params["center_x_singlepix"] = float(self.center_x_singlepix.text())
        params["center_y_singlepix"] = float(self.center_y_singlepix.text())
        params["center_z_singlepix"] = float(self.center_z_singlepix.text())

        functions.write_parameters(params)

        last_event = functions.update_event_log('Parameters saved.')
        self.info_box.setText(last_event)

    def plot_data(self):
        last_event = functions.plotting_data()
        self.info_box.setText(last_event)

    def save_data(self):
        last_event = functions.saving_data()
        self.info_box.setText(last_event)

    def cleanup(self):
        """
        Method handling the aboutToQuit() signal from the main application by
        running the stage's shutdown method (shut the connection to the stage
        down cleanly).
        """
        if self.stage:
            self.stage.shutdown()
            self.stage = None
        self.pushButton_conn_piezos.setStyleSheet("background-color: lightgrey;")


def main():
    """Set scaling factor for good sizing and dpi of gui"""
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = mywindow()
    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

    app.aboutToQuit.connect(main.cleanup)
    app.aboutToQuit.connect(app.deleteLater)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
