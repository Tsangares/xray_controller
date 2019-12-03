import os,time,math,sys
from shutil import copyfile

def save(folder,CWD='E:\\'):
	if folder == "" or folder is None:
		folder=str(math.floor(time.time()))
	CONTROLLER=os.path.join(CWD,'controller')
	STATIC=os.path.join(CONTROLLER,'static')
	DATA=os.path.join(CWD,'data')
	outputFolder=os.path.join(DATA,folder)
	plotFolder=os.path.join(outputFolder,'images')
	metaFolder=os.path.join(outputFolder,'meta')
	binaryFolder=os.path.join(outputFolder,'binary')
	print("Creating folder",outputFolder)
	os.mkdir(outputFolder)
	os.mkdir(plotFolder)
	os.mkdir(metaFolder)
	os.mkdir(binaryFolder)

	images=[f for f in os.listdir(STATIC) if '.png' in f]
	txts=[f for f in os.listdir(CWD) if '.txt' in f]
	waves=[f for f in os.listdir(CONTROLLER) if '.dat' in f and 'wave' in f]

	for wave in waves:
		copyfile(os.path.join(CONTROLLER,wave), os.path.join(binaryFolder,wave))
	for image in images:
	    copyfile(os.path.join(STATIC,image),os.path.join(plotFolder,image))
	for txt in txts:
	    copyfile(os.path.join(CWD,txt),os.path.join(metaFolder,txt))
	print("======== SAVE COMPLETED =========")

if __name__=='__main__':
	folder=input("Enter a folder name (empty for unix time): ")
	save(folder)
