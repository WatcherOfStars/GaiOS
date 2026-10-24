import dearpygui.dearpygui as dpg
import MQTT_client as mqtt
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
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (50,200,75), category=dpg.mvThemeCat_Core)
    dpg.bind_theme(global_theme)

setup_theme()

randomDataIterations = 1
def addRandomData(sender, app_data):
    for x in range(randomDataIterations):
        fake_data.addRandomData()

def refreshData(sender, add_data):
    update_all_data()
    dpg.set_value("log", str(data_source.serializeCurrentData()))

def toggleFullscreen(sender, add_data):
    dpg.toggle_viewport_fullscreen()

with dpg.window(label="DATA", width=800, height=350, pos=(0,0)):
    with dpg.group(horizontal=True):
        dpg.add_button(label="Refresh data", callback=refreshData)
        dpg.add_button(label="Add random data", callback=addRandomData)
        dpg.add_button(label="Toggle fullscreen", callback=toggleFullscreen)
    #create_menu_bar()
    with dpg.child_window(tag="scroll_window", horizontal_scrollbar=True):
        pass

with dpg.window(label="LOG", width=800, height=90, pos=(0,350)):
    dpg.add_text("None", tag="log")

dpg.create_viewport(title="Autoponics Control GUI", width=800,height=480)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.toggle_viewport_fullscreen()

#data_source = fake_data
data_source = mqtt

def add_device(device_obj):
    print("Device name: " + device_obj.name)
    with dpg.collapsing_header(indent=0, parent="scroll_window", label=device_obj.name, tag="device_group_"+device_obj.name, default_open = True):
        pass
        with dpg.group(horizontal= True, tag="device_group_"+device_obj.name+"_horizontal"):
            pass
    
def add_data_plot(device_obj, data_obj):
    #create lable and graph
    #with dpg.group(indent=40, parent="device_group_"+device_obj.name+"_horizontal"):
    with dpg.plot(label=data_obj.dataType, height=250, width=250, parent="device_group_"+device_obj.name+"_horizontal"):
        #dpg.add_plot_legend()
        plot_name = str("device_group_"+device_obj.name+"data_group_"+data_obj.dataType)
        # create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="time", tag=plot_name+"_time")
        dpg.add_plot_axis(dpg.mvYAxis, label=data_obj.dataType, tag=plot_name+"_value")

        # series belong to a y axis
        dpg.add_line_series(data_obj.times, data_obj.values, label=data_obj.dataType, tag=plot_name, parent=plot_name+"_value")
        dpg.fit_axis_data(plot_name+"_value")
        dpg.fit_axis_data(plot_name+"_time")

def update_data_plot(device_obj, data_obj):
    plot_name = str("device_group_"+device_obj.name+"data_group_"+data_obj.dataType)
    print("Values: ", data_obj.values)
    print("Times: ", data_obj.times)
    dpg.set_value(plot_name, [data_obj.times, data_obj.values])
    dpg.fit_axis_data(plot_name+"_value")
    dpg.fit_axis_data(plot_name+"_time")


def update_all_data():
    data_source.update_data()

    #for all devices
    for d in data_source.devices:
        device_obj = data_source.devices[d]
        #create device if needed
        if not dpg.does_item_exist("device_group_"+device_obj.name):
            add_device(device_obj)

        #for all data plots of device
        for i in device_obj.dataPoints:
            data_obj = device_obj.dataPoints[i]
            #add or update data plot
            if not dpg.does_item_exist("device_group_"+device_obj.name+"data_group_"+data_obj.dataType):
                add_data_plot(device_obj, data_obj)
            else:
                update_data_plot(device_obj, data_obj)

last_data_timestamp = datetime.now().timestamp()
update_time = 5 #seconds
while dpg.is_dearpygui_running():
    if (datetime.now().timestamp() - last_data_timestamp >= update_time):
        last_data_timestamp = datetime.now().timestamp()
        update_all_data()
        dpg.set_value("log", str(data_source.serializeCurrentData()))
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()