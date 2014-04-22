# Maya to Sketchfab exporter
# v2014_04_22
# www.ticket01.com | Matthias F. Richter

import tempfile, os, json, base64, urllib2, zipfile
from pymel.core import *
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

def uploadButtonPressed(title, description, tags, api_key, upload_status):

	optionVar['maya2sketchfab_title'] = title.getText()
	optionVar['maya2sketchfab_description'] = description.getText()
	optionVar['maya2sketchfab_tags'] = tags.getText()
	optionVar['maya2sketchfab_api_key'] = api_key.getText()

	# create a temporary directory 
	tmp_dir = tempfile.mkdtemp()
	base_name = '%s/maya2sketchfab' % tmp_dir
	file_name = '%s.obj' % base_name
	# for some reason Maya fails to export to this location when the file does not yet exist
	# create a dummy file with zero length that has the same name
	open(file_name, 'w').close()
	# export Maya scene as Wavefront .obj
	exportAll(file_name, force=True, type='OBJ')
	# create a screen shot and save as .png
	thumb_file_name = '%s.png' % base_name
	buffer = om.MImage()
	omui.M3dView.active3dView().readColorBuffer(buffer, True)
	buffer.resize(448, 280, True)
	buffer.writeToFile(thumb_file_name, 'png')
	files = os.listdir(tmp_dir)
	# create .zip file that includes the .obj and the .mtl
	obj_mtl_archive_name = '%s.zip' % base_name
	obj_mtl_archive = zipfile.ZipFile(obj_mtl_archive_name, 'w')
	for f in files:
		obj_mtl_archive.write('%s/%s' % (tmp_dir, f), f, zipfile.ZIP_DEFLATED)
	obj_mtl_archive.close()
	# encode file contents to base64
	f = open(obj_mtl_archive_name, 'rb')
	contents_base64 = base64.encodestring(f.read())
	f.close()
	f = open(thumb_file_name, 'rb')
	thumb_base64 = base64.encodestring(f.read())
	f.close()
	# get Maya version
	maya_version = about(v=True)

	data = {
		'title': title.getText(),
		'description': description.getText(),
		'contents': contents_base64,
		'filename': obj_mtl_archive_name,
		'tags': tags.getText(),
		'token': api_key.getText(),
		'thumbnail': thumb_base64,
		'source': maya_version
	}
	
	# first pass without payload to overcome a problem with 'first contact'
	try:
		f = urllib2.urlopen('https://api.sketchfab.com/model')
	except:
		pass	
	f.close()
	
	response = ''
	try:
		f = urllib2.urlopen('https://api.sketchfab.com/model', data=json.dumps(data))
		response = f.read()
	except:
		pass		
	f.close()
	upload_status.setLabel('Last upload: Failed!') if response.rfind('"success": true') == -1 else upload_status.setLabel('Last upload: Successful!')	

def createMaya2SketchFabUI():
	maya2sf_window = window(title='Sketchfab Uploader')
	fl = formLayout()
	txt_explanation = text(label='This dialog uploads the currently open scene to Sketchfab.com. All fields marked with * are mandatory. After registration on Sketchfab.com you can get your API key from your account.', height=40, align='left', wordWrap=True)
	txt_title = text(label='Title *', align='left')
	tf_title = textField()
	tf_title.setText(optionVar['maya2sketchfab_title'] if optionVar.has_key('maya2sketchfab_title') else '')
	txt_description = text(label='Description', align='left')
	sf_description = scrollField(numberOfLines=5)
	sf_description.setText(optionVar['maya2sketchfab_description'] if optionVar.has_key('maya2sketchfab_description') else '')
	txt_tags = text(label='Tags (separate with spaces)', align='left')
	tf_tags = textField()
	tf_tags.setText(optionVar['maya2sketchfab_tags'] if optionVar.has_key('maya2sketchfab_tags') else '')
	txt_api_key = text(label='API key *', align='left')
	tf_api_key = textField()
	tf_api_key.setText(optionVar['maya2sketchfab_api_key'] if optionVar.has_key('maya2sketchfab_api_key') else '')
	bt_ticket01 = button(label='Sketchfab Uploader by ticket01.com')
	bt_ticket01.setCommand('showHelp("http://www.ticket01.com", a=True)')
	bt_upload = button(label='Upload to Sketchfab')
	txt_upload_status = text(label='Last upload: Nothing upladed, yet ;)', align='left')
	bt_upload.setCommand(Callback(uploadButtonPressed, tf_title, sf_description, tf_tags, tf_api_key, txt_upload_status), height=50)
	
	fl.attachForm(txt_explanation, 'left', 10)
	fl.attachForm(txt_explanation, 'top', 20)
	fl.attachForm(txt_explanation, 'right', 10)
	
	fl.attachForm(txt_title, 'left', 10)
	fl.attachForm(txt_title, 'right', 10)
	fl.attachControl(txt_title, 'top', 20, txt_explanation)

	fl.attachForm(tf_title, 'left', 10)
	fl.attachForm(tf_title, 'right', 10)
	fl.attachControl(tf_title, 'top', 5, txt_title)

	fl.attachForm(txt_description, 'left', 10)
	fl.attachForm(txt_description, 'right', 10)
	fl.attachControl(txt_description, 'top', 5, tf_title)

	fl.attachForm(sf_description, 'right', 10)
	fl.attachForm(sf_description, 'left', 10)
	fl.attachControl(sf_description, 'top', 5, txt_description)

	fl.attachForm(txt_tags, 'left', 10)
	fl.attachForm(txt_tags, 'right', 10)
	fl.attachControl(txt_tags, 'top', 5, sf_description)

	fl.attachForm(tf_tags, 'right', 10)
	fl.attachForm(tf_tags, 'left', 10)
	fl.attachControl(tf_tags, 'top', 5, txt_tags)

	fl.attachForm(txt_api_key, 'left', 10)
	fl.attachForm(txt_api_key, 'right', 10)
	fl.attachControl(txt_api_key, 'top', 5, tf_tags)

	fl.attachForm(tf_api_key, 'right', 10)
	fl.attachForm(tf_api_key, 'left', 10)
	fl.attachControl(tf_api_key, 'top', 5, txt_api_key)

	fl.attachForm(bt_upload, 'right', 10)
	fl.attachForm(bt_upload, 'left', 10)
	fl.attachControl(bt_upload, 'top', 20, tf_api_key)

	fl.attachControl(bt_ticket01, 'top', 10, bt_upload)
	fl.attachForm(bt_ticket01, 'bottom', 10)
	fl.attachForm(bt_ticket01, 'right', 10)
	
	fl.attachControl(txt_upload_status, 'top', 10, bt_upload)
	fl.attachForm(txt_upload_status, 'bottom', 10)
	fl.attachForm(txt_upload_status, 'left', 10)

	maya2sf_window.setWidth(512)
	maya2sf_window.setHeight(432)
	maya2sf_window.setSizeable(False)
	maya2sf_window.show()

createMaya2SketchFabUI()