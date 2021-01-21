import os
import xml.etree.ElementTree as ET
gt_dirs = ["/Users/hanlinwang/Desktop/thesis3/NEW/WTGProject/PythonServer/all_data/GT/test/"]
gt_xml_dirs = "/Users/hanlinwang/Desktop/thesis3/NEW/WTGProject/PythonServer/all_data/XML/"
paladin_dirs = [""]

'''
edges
1:Type {#, LongClick, Dialog, OptionsMenu, Mannul}
2:TimeStamp
2.5:Event {Menu, Back}
3:SourceActivity
4:x
5:y
6:Widget
7:WidgetID

edges_dict (#)
0: Type		 //key
1: TimeStamp //key
2,3: Event/SourceActivity
4,5: x,y
6: Widget
7: WidgetID


windows
1: Type {Dialog, OptionsMenu, Activity}
2: Content {Title, List, Name}
'''

#windows = [{"Type":"Dialog","ID":0,"Title":""}] 

def read_raw_log(file):
	raw_list = []
	print(file)
	current_file = open(file,'r')
	lines = current_file.readlines()

	for line in lines:
		attributes = line.split("\\n")
		if ("#" == attributes[0]):
			current_timestamp = int(attributes[1])
			current_event = "NONE"
			current_activity = ""
			current_x = -1
			current_y = -1
			current_widget = ""
			current_widgetID = ""
			for attribute in attributes[2:len(attributes)]:
				if "Event:" == attribute[:6]:
					current_event = attribute[6:]
				elif "SourceActivity:" == attribute[:15]:
					current_activity = attribute[15:]
				elif "x:" == attribute[:2] :
					current_x = float(attribute[2:])
				elif "y:" == attribute[:2] :
					current_y = float(attribute[2:])
				elif "Widget:" == attribute[:7]:
					current_widget = attribute[7:].split('{')[0]
				elif "WidgetID:" == attribute[:9]:
					current_widgetID = attribute[9:]
				elif '\n' != attribute:
					print("Warning Unknow data:" + attribute)
			
			current_dict = dict( [("Type","#"), ("TimeStamp",current_timestamp), ("Event", current_event), ("Activity", current_activity), ("x", current_x), ("y", current_y),
					("Widget", current_widget), ("WidgetID", current_widgetID)] )
			raw_list.append(current_dict)

		elif ("Dialog" == attributes[0]):
			current_timestamp = int(attributes[1])
			current_activity = ""
			current_title = ""
			current_stacks = ""
			current_list = ""
			for attribute in attributes[2:len(attributes)]:
				if "SourceActivity:" == attribute[:15]:
					current_activity = attribute[15:]
				elif "Title:" == attribute[:6]:
					current_title = attribute[6:]
				elif "List:" == attribute[:5]:
					current_list = attribute[5:]
					current_list = current_list[1:-1].split(", ")
				elif "Stacks:" == attribute[:7]:
					current_stacks = attribute[7:]
				elif '\n' != attribute:
					print("Warning Unknow data:" + attribute)
			current_dict = dict( [("Type","Dialog"), ("TimeStamp",current_timestamp), ("Activity", current_activity), ("Title", current_title), ("List", current_list),
			("Stacks", current_stacks) ] )
			
			raw_list.append(current_dict)
		
		elif ("LongClick" == attributes[0]):
			current_timestamp = int(attributes[1])
			current_activity = ""
			current_widget = ""
			current_widgetID = ""
			for attribute in attributes[2:len(attributes)]:
				if "SourceActivity:" == attribute[:15]:
					current_activity = attribute[15:]
				elif "Widget:" == attribute[:7]:
					current_widget = attribute[7:].split('{')[0]
				elif "WidgetID:" == attribute[:9]:
					current_widgetID = attribute[9:]
				elif '\n' != attribute:
					print("Warning Unknow data:" + attribute)
			current_dict = dict( [("Type","LongClick"), ("TimeStamp",current_timestamp), ("Activity", current_activity), 
				("Widget", current_widget), ("WidgetID", current_widgetID)] )
			raw_list.append(current_dict)

		elif ("OptionsMenu" == attributes[0]):

			current_timestamp = int(attributes[1])
			current_activity = ""
			current_list = ""
			for attribute in attributes[2:len(attributes)]:
				if "SourceActivity:" == attribute[:15]:
					current_activity = attribute[15:]
				elif "List:" == attribute[:5]:
					current_list = attribute[5:]
					current_list = current_list[1:-1].split(", ")

				elif '\n' != attribute:
					print("Warning Unknow data:" + attribute)

			current_dict = 	dict( [("Type","OptionsMenu"), ("TimeStamp",current_timestamp), ("Activity", current_activity), 
				("List", current_list)] )
			raw_list.append(current_dict)

		elif ("Mannul" == attributes[0]):
			current_timestamp = int(attributes[1])
			current_activity = ""
			for attribute in attributes[2:len(attributes)]:
				if "SourceActivity:" == attribute[:15]:
					current_activity = attribute[15:]
				elif '\n' != attribute:
					print("Warning Unknow data:" + attribute)					

			current_dict = 	dict( [("Type","Mannul"), ("TimeStamp",current_timestamp), ("Activity", current_activity), ("Event","NONE")] )
			raw_list.append(current_dict)
	return raw_list

def sort_raw_list(raw_list):
	return sorted(raw_list, key = lambda x:(x["TimeStamp"],x["Type"]) )

def Check_Menu(temp_link, window_list):
	if 'x' not in temp_link or 'y' not in temp_link:
		return False
	current_text = Get_Text_FromViewTree(temp_link)
	for window in window_list:
		if window["Type"] == "Menu":
			if "List" in window:
				for ti in window["List"]:
					if current_text == ti:
						#It is a click on a menu
						return True
	return False

def create_windows(raw_list, index, window_list, temp_link):
	'''
	Windows
	1: Type {Dialog, Menu, Activity}
	2: Content {Title, ActivityName, Name}'''
	window_dict = {}
	source_dict = raw_list[index]
	if (index > 0):
		if raw_list[index-1]["Type"] == "LongClick":
			if window_list!=None and temp_link!=None and Check_Menu(temp_link, window_list):
				# It is on a menu window
				window_dict["Type"] = "Menu"
				window_dict["Content"] = source_dict["Activity"]
				return window_dict
			elif index > 1:
				# It is on a dialog window
				if raw_list[index-2]["Type"] == "Dialog":
					window_dict["Type"] = "Dialog"
					window_dict["Content"] = raw_list[index-2]["Title"]
					return window_dict
			# It is on a activity window
			window_dict["Type"] = "Activity"
			window_dict["Content"] = source_dict["Activity"]
			return window_dict

	j = index + 1
	if (j >= len(raw_list) or raw_list[j]["Type"] == '#' or raw_list[j]["Type"] == 'Mannul'):
		# if i >= length of list, it is last link 
		if window_list!=None and temp_link!=None and Check_Menu(temp_link, window_list):
			# It is on a menu window
			window_dict["Type"] = "Menu"
			window_dict["Content"] = source_dict["Activity"]
			return window_dict
		elif source_dict["Event"] == "MENU":
			# it invoke system event Menu 
			window_dict["Type"] = "Activity"
			window_dict["Content"] = source_dict["Activity"]
		else:
			# it is a Activity window
			window_dict["Type"] = "Activity"
			window_dict["Content"] = source_dict["Activity"]
	elif (raw_list[j]["Type"] == "Dialog"):
		# it is a Dialog window
		window_dict["Type"] = "Dialog"
		window_dict["Content"] = raw_list[j]["Title"]
	elif (raw_list[j]["Type"] == "OptionsMenu"):
		# it generate a optionsmenu
		window_dict["Type"] = "Activity"
		window_dict["Content"] = source_dict["Activity"]
	else:
		print("Warning no window found at:" + str(source_dict) )
		
	return window_dict

def Check_Link(link, linklist):
	if link["Type"] == "Mannul":
		for j in linklist:
			if (j["Type"] == link["Type"] and j["SourceWindow"] == link["SourceWindow"] and j["TargetWindow"] == link["TargetWindow"]):
				return False
		return True
	else:
		for j in linklist:
			if (j["Type"] == link["Type"] and j["SourceWindow"] == link["SourceWindow"] and j["TargetWindow"] == link["TargetWindow"]
				 and j["Widget"] == link["Widget"] and j["WidgetID"] == link["WidgetID"] and j["ViewTree"] == link["ViewTree"]):
				return False
		return True

def ViewTree_Recursion(tree,x,y):
	viewtree = ""
	for child in tree:
		temp = child.attrib["bounds"].split("][")[0][1:]
		x1 = int(temp.split(',')[0])
		y1 = int(temp.split(',')[1])
		temp = child.attrib["bounds"].split("][")[1][:-1]
		x2 = int(temp.split(',')[0])
		y2 = int(temp.split(',')[1])

		if (x1<=x and x2>=x and y1<=y and y2>=y):
			viewtree = child.attrib["class"] + '/' + child.attrib["index"] + '/' + ViewTree_Recursion(child,x,y)
			return viewtree
	return ""
def Get_ViewTree(temp_link):
	try:
		mytree = ET.parse(gt_xml_dirs + app_name + os.path.sep + str(temp_link["TimeStamp"]) + ".xml")
		myroot = mytree.getroot()
		x = temp_link['x']
		y = temp_link['y']
		if (x==-1 or y==-1):
			return ""
		
		#print(temp_link)
		viewtree = ViewTree_Recursion(myroot,x,y)
		#print(viewtree)
		return viewtree
	except FileNotFoundError:
		print("==================================")
		print("Error: This XML file not found" + gt_xml_dirs + app_name + os.path.sep + str(temp_link["TimeStamp"]) + ".xml")
		print("Belong to this edge")
		print(temp_link)
		print("==================================")
		return "NONE"

def ViewTree_Recursion_Text(tree,x,y):
	viewtree = None
	for child in tree:
		temp = child.attrib["bounds"].split("][")[0][1:]
		x1 = int(temp.split(',')[0])
		y1 = int(temp.split(',')[1])
		temp = child.attrib["bounds"].split("][")[1][:-1]
		x2 = int(temp.split(',')[0])
		y2 = int(temp.split(',')[1])

		if (x1<=x and x2>=x and y1<=y and y2>=y):
			viewtree = ViewTree_Recursion_Text(child,x,y)
			if viewtree == None:
				if ("text" in child.attrib):

					return child.attrib["text"]
				else:
					return ""
			else:
				return viewtree
	if ("text" in tree.attrib):

		return tree.attrib["text"]
	else:
		return ""

def Get_Text_FromViewTree(temp_link):
	try:
		mytree = ET.parse(gt_xml_dirs + app_name + os.path.sep + str(temp_link["TimeStamp"]) + ".xml")
		myroot = mytree.getroot()
		x = temp_link['x']
		y = temp_link['y']
		if (x==-1 or y==-1):
			return ""
		viewtree = ViewTree_Recursion_Text(myroot,x,y)
		return viewtree
	except FileNotFoundError:
		print("==================================")
		print("Error: This XML file not found" + gt_xml_dirs + app_name + os.path.sep + str(temp_link["TimeStamp"]) + ".xml")
		print("Belong to this edge")
		print(temp_link)
		print("==================================")
		return "NONE"

def Identify_Link(raw_list, i, last_dict, current_dict, current_type, last_timestamp):
	link = {}
	if "Widget" in current_dict:
		# last_dict is not Mannul
		link["Type"] = current_type
		for k in current_dict:
			if k == "TimeStamp":
				link[k] = last_timestamp
				last_timestamp = current_dict["TimeStamp"]
			elif k == "Widget":
				link[k] = current_dict[k]
			elif k == "WidgetID":
				link[k] = current_dict[k]
			elif k == 'x':
				link[k] = current_dict[k]
			elif k == 'y':
				link[k] = current_dict[k]		
	else:
		# last_dict is Mannul
		link["Type"] = "Mannul"
		for k in last_dict:
			if k == "TimeStamp":
				link[k] = last_timestamp
				last_timestamp = current_dict["TimeStamp"]

	return link,last_timestamp

def Identify_Window(window_list, last_window):
	i = 0
	for key in window_list:
		if key["Type"] == last_window["Type"] and key["Content"] == last_window["Content"]:
			return i
		i = i + 1
	return -1
def create_links(raw_list):
	''' There are 8 types of links can exploit from Promal, 
		including #, # with Event Back, #+Dialog, #+Dialog+LongClick, #+LongClick, # with Event Menu, # with Event Menu+OptionsMenu, Mannul
	'''
	c_edge_list = []
	c_window_list = []
	last_dict = raw_list[0]
	if "Mannul" == last_dict["Type"]:
		current_type = "Mannul"
	elif "#" == last_dict["Type"]:
		if last_dict["Event"]!="NONE":
			current_type = last_dict["Event"]
			if current_type == "BACK":
				print("Warning a BACK behavior at the log beginning which should be wrong")
		else:
			current_type = "Click"
	elif "Dialog" == last_dict["Type"]:
		# if app show a dialog before anything else
		current_type = "NONE"
	else:
		current_type = "NONE"
	
	last_window = create_windows(raw_list, 0, None, None)
	c_window_list.append(last_window)

	last_timestamp = last_dict["TimeStamp"]
	i = 1
	#print(last_dict)
	while (i < len(raw_list)):
		current_dict =  raw_list[i]
		#print(current_dict)

		if current_dict["Type"] == "#":
			# new link
			if (raw_list[i-1]["Type"] == "LongClick"):
				current_type = "LongClick"
			temp_link, last_timestamp = Identify_Link(raw_list, i, last_dict, current_dict, current_type, last_timestamp)
			temp_link["SourceWindow"] = last_window
			last_window = create_windows(raw_list, i, c_window_list, temp_link)
			temp_link["TargetWindow"] = last_window
			
			if temp_link["Type"]!="Mannul":
				viewtree = Get_ViewTree(temp_link)
				temp_link["ViewTree"] = viewtree

			last_dict = current_dict

			# Identify if this window already in list
			if Identify_Window(c_window_list, last_window) == -1:
				c_window_list.append(last_window)
			if Check_Link(temp_link, c_edge_list):
				c_edge_list.append(temp_link)


			if current_dict["Event"] == "BACK":
				current_type = "Back"
			else:
				current_type = "Click"

		elif current_dict["Type"] == "Dialog":
			if (i+1 < len(raw_list)) and (raw_list[i+1]["Type"] == "LongClick"):

				i = i
				#print(current_dict["TimeStamp"] == raw_list[i+1]["TimeStamp"])

				#quit()
			# it isn't a link
			#last_timestamp = current_dict["TimeStamp"]
		elif current_dict["Type"] == "OptionsMenu" or current_dict["Type"] == "ContextMenu":

			menu_window = {"Type":"Menu", "Content":current_dict["Activity"],"List": current_dict["List"]}
			index_w = Identify_Window(c_window_list, menu_window)
			if index_w == -1:
				c_window_list.append(menu_window)
			else:
				last_menu = c_window_list.pop(index_w)
				if "List" in last_menu:
					last_list = last_menu["List"]
				else:
					last_list = []
				menu_list = menu_window["List"]
				for ti in last_list:
					if not ti in menu_list:
						menu_list.append(ti)
				c_window_list.append(menu_window)
			# it isn't a link, its timestamp will be same as previous one
			#last_timestamp = current_dict["TimeStamp"]
			i = i
		elif current_dict["Type"] == "LongClick":
			# it is a LongClick Event, its timestamp will be same as previous one
			i = i

		elif current_dict["Type"] == "Mannul":
			# new link
			temp_link, last_timestamp = Identify_Link(raw_list, i, last_dict, current_dict, current_type, last_timestamp)
			temp_link["SourceWindow"] = last_window
			last_window = create_windows(raw_list, i, c_window_list, temp_link)
			temp_link["TargetWindow"] = last_window
			last_dict = current_dict
			if  temp_link["Type"]!="Mannul" :
				viewtree = Get_ViewTree(temp_link)
				temp_link["ViewTree"] = viewtree

			# Identify if this window already in list
			if Identify_Window(c_window_list, last_window) == -1:
				c_window_list.append(last_window)
			if Check_Link(temp_link, c_edge_list):
				c_edge_list.append(temp_link)
			
			current_type = "Mannul"
		else:
			print("Warning Unknow type:" + current_dict)

		i = i + 1

	return c_edge_list, c_window_list

total = 0
size = 0
current_raw_list = []
edge_list = []
window_list = []
max_windows = 0
min_windows = 999999
total_windows = 0
app_name = ""

for current_dir in gt_dirs:
	for file in os.listdir(current_dir):
		if file.endswith(".log"):
			app_name = file[:-4]
			current_raw_list = read_raw_log(current_dir + file)
			current_raw_list = sort_raw_list(current_raw_list)
			edge_list,window_list = create_links(current_raw_list);
			
			
			
'''				# Dialog edges
				if ("Dialog" == attributes[0]):
					title_bool = False
					for attribute in attributes:
						if ("Title:" in attribute):
							current_dialog_title = attribute.split("Title:")[1]
							current_dict = dict( [("Type","Dialog"), ("Content",current_dialog_title)] )
							
							if (current_dict not in windows):
								windows.append(current_dict)
							title_bool = True
					if (not title_bool):
						current_dict = dict( [("Type","Dialog"), ("Content","NONE")] )
						if (current_dict not in windows):
							windows.append(current_dict)

				elif ("OptionsMenu" == attributes[0]):
					for attribute in attributes:
						if ("List:" in attribute):
							current_menu_list = attribute.split("List:")[1]
							current_dict = dict( [("Type","Menu"), ("Content",current_menu_list)] )

							if (current_dict not in windows):
								windows.append(current_dict)					

				for attribute in attributes:
					# add activities windows
					if ("SourceActivity:" in attribute):
						current_activity = attribute.split("SourceActivity:")[1]
						current_dict = dict( [("Type","Activity"), ("Content",current_activity)] )
						
						if (current_dict not in windows):
							windows.append(current_dict)
				#print(attributes[0])

			total_windows = total_windows + len(windows)
			if len(windows) < min_windows:
				min_windows = len(windows)
			if len(windows) > max_windows:
				max_windows = len(windows)

			window_list.append(windows)
			print(windows)


			

edge_list.sort()
print("Edges Medium", edge_list[len(edge_list)//2])
print("Edges Average:",total/size)
print("Total apps",size)

print("Windows Average:", total_windows/size)
print("Max Windows:", max_windows)
print("Min Windows:", min_windows)

'''