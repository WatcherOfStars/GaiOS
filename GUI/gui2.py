import dearpygui.dearpygui as dpg
#import MQTT_client as mqtt
import DB_fake_data as fake_data
from datetime import datetime


dpg.create_context()

#DPG THEME
#create menu bar at top of window
def create_menu_bar():
    with dpg.menu_bar():
        with dpg.menu(label="Tools"): #some tools dearpy provides
                dpg.add_menu_item(label="Show About", callback=lambda:dpg.show_tool(dpg.mvTool_About))
                dpg.add_menu_item(label="Show Metrics", callback=lambda:dpg.show_tool(dpg.mvTool_Metrics))
                dpg.add_menu_item(label="Show Documentation", callback=lambda:dpg.show_tool(dpg.mvTool_Doc))
                dpg.add_menu_item(label="Show Debug", callback=lambda:dpg.show_tool(dpg.mvTool_Debug))
                dpg.add_menu_item(label="Show Style Editor", callback=lambda:dpg.show_tool(dpg.mvTool_Style))
                dpg.add_menu_item(label="Show Font Manager", callback=lambda:dpg.show_tool(dpg.mvTool_Font))
                dpg.add_menu_item(label="Show Item Registry", callback=lambda:dpg.show_tool(dpg.mvTool_ItemRegistry))

        with dpg.menu(label="Settings"): #some basic settings
            dpg.add_menu_item(label="Wait For Input", check=True, callback=lambda s, a: dpg.configure_app(wait_for_input=a))
            dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda:dpg.toggle_viewport_fullscreen())

#sets up theme colors and styles
def setup_theme():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (25,175,50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, (25,175,50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (50,200,75), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (50,200,75), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (80, 230, 120), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (50,200,75), category=dpg.mvThemeCat_Core)
    dpg.bind_theme(global_theme)

setup_theme()

#quck access button callbacks
randomDataIterations = 1
def addRandomData(sender, app_data):
    for x in range(randomDataIterations):
        fake_data.addRandomData()

def refreshData(sender, add_data):
    update_all_data()
    dpg.set_value("log", str(data_source.serializeCurrentData()))

def toggleFullscreen(sender, add_data):
    dpg.toggle_viewport_fullscreen()

#create main window
with dpg.window(label="DATA", width=800, height=480, pos=(0,0), on_close=lambda:dpg.stop_dearpygui()):
    create_menu_bar()
    #buttons at top of window
    with dpg.group(horizontal=True):
        dpg.add_button(label="Refresh data", callback=refreshData)
        dpg.add_button(label="Add random data", callback=addRandomData)
        dpg.add_button(label="Toggle fullscreen", callback=toggleFullscreen)

    #create main area with subdivisions
    with dpg.group(horizontal=True):
        with dpg.child_window(tag="device_window", horizontal_scrollbar=True, width=150):
            pass
        with dpg.group(width=400):
            with dpg.child_window(tag="scroll_window", horizontal_scrollbar=True, height=300):
                pass
            with dpg.child_window(tag="log_window", height=90):
                dpg.add_text("None", tag="log")
        with dpg.child_window(tag="control_window", horizontal_scrollbar=True, width=250):
            pass

#start dpg
dpg.create_viewport(title="Autoponics Control GUI", width=800,height=480)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.toggle_viewport_fullscreen()

data_source = fake_data
#data_source = mqtt

#current device getter/setter
_current_device = None
def get_current_device():
    return _current_device
def set_current_device(device):
    global _current_device
    _current_device = device
    

#button callback, loads clicked device's data into main window
def load_device(sender, app_data):
    #set current device from button tag
    set_current_device(sender.replace("device_button_", ""))
    print("Loading device: ", get_current_device())
    #clear data window
    dpg.delete_item("scroll_window", children_only=True)
    #create new data window
    with dpg.group(tag="device_group_"+get_current_device()+"_horizontal", parent="scroll_window"):
        dpg.add_text("Device: "+get_current_device())
        dpg.add_separator()
    #populate data window with data plots
    update_all_data()

#adds a button for a device to the device window
def add_device(device_obj):
    print("Device name: " + device_obj.name)
    dpg.add_button(label=device_obj.name, parent="device_window", tag="device_button_"+device_obj.name, callback=load_device, width=130, height=25)
    
#adds a data plot to the data window for given device and data type
def add_data_plot(device_obj, data_obj):
    #create lable and graph
    #with dpg.group(indent=40, parent="device_group_"+device_obj.name+"_horizontal"):
    with dpg.plot(label=data_obj.dataType, height=270, width=360, parent="device_group_"+device_obj.name+"_horizontal"):
        #dpg.add_plot_legend()
        plot_name = str("device_group_"+device_obj.name+"data_group_"+data_obj.dataType)
        # create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="time", tag=plot_name+"_time")
        dpg.add_plot_axis(dpg.mvYAxis, label=data_obj.dataType, tag=plot_name+"_value")

        # series belong to a y axis
        dpg.add_line_series(data_obj.times, data_obj.values, label=data_obj.dataType, tag=plot_name, parent=plot_name+"_value")
        dpg.fit_axis_data(plot_name+"_value")
        dpg.fit_axis_data(plot_name+"_time")

#updates an existing data plot with new data
def update_data_plot(device_obj, data_obj):
    plot_name = str("device_group_"+device_obj.name+"data_group_"+data_obj.dataType)
    print("Values: ", data_obj.values)
    print("Times: ", data_obj.times)
    dpg.set_value(plot_name, [data_obj.times, data_obj.values])
    dpg.fit_axis_data(plot_name+"_value")
    dpg.fit_axis_data(plot_name+"_time")

#updates all data from data source, adds new devices/plots as needed
def update_all_data():
    data_source.update_data()
    print("Current device: ", get_current_device())
    dpg.set_value("log", str(data_source.serializeCurrentData()))
    #for all devices
    for d in data_source.devices:
        device_obj = data_source.devices[d]
        #create device if needed
        if not dpg.does_item_exist("device_button_"+device_obj.name):
            print("Adding device: ", device_obj.name)
            add_device(device_obj)
        #return and don't plot if not the current device
        if device_obj.name != get_current_device():
            continue
        #for all data plots of device
        for i in device_obj.dataPoints:
            print("Updating plot: ", device_obj.name)
            data_obj = device_obj.dataPoints[i]
            #add or update data plot
            if not dpg.does_item_exist("device_group_"+device_obj.name+"data_group_"+data_obj.dataType):
                add_data_plot(device_obj, data_obj)
            else:
                update_data_plot(device_obj, data_obj)
    

last_data_timestamp = datetime.now().timestamp()
update_time = 5 #seconds

#main loop
while dpg.is_dearpygui_running():
    # if (datetime.now().timestamp() - last_data_timestamp >= update_time):
    #     last_data_timestamp = datetime.now().timestamp()
    #     update_all_data()
    #     dpg.set_value("log", str(data_source.serializeCurrentData()))
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()