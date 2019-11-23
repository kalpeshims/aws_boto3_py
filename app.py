from flask import Flask, render_template, url_for, request
import boto3
import zipfile
import os

iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')

app = Flask(__name__)

class ResourceConflictException(Exception): pass


@app.route('/')
def index():
   return render_template('index.html')

# role = iam_client.get_role(RoleName='FullAccess-Lambda-DynamoDB')
# print(role)
@app.route('/', methods=['POST'])

def getvalue():
	#print(request.files['zipCode']);
	#print ("XXHHH",request.form)
	#print ("XXHHH",request.method)
	##if 'fileUpload' in request.files:
	fileUpload=request.files['photo']
	#print (fileUpload)
	fileUpload.save(os.path.join('files/', fileUpload.filename))

    
    # if 'fileUpload' in request.files:
    # 		fileUpload=request.files['photo']
    # 		print (fileUpload)    
	funName=request.form['funName']
	funName=funName.replace(" ", "-")
	runTime=request.form['runTime'] #"nodejs10.x"
	role=request.form['role'] #"arn:aws:iam::112911278656:role/proximity-serverless-dev-us-east-1-lambdaRole"
	handler=request.form['handler'] #"main.handler"
	#fileCode=request.form['fileCode'] #"Hello test file write"
	ltype=request.form['ltype'] #"Hello test file write"
	event=request.form['event']
	Timeout=300

	if event == "":
		event = "{}"
	
	# create folder,file and write code into folder
	# strnew=handler.split(".",2)
	# filename=strnew[0] + ".js"
	# zipFileName=funName + ".zip"
	zipFileName=fileUpload.filename
	fileCode='files/' + fileUpload.filename


	zipped_code = fileProcess(fileUpload.filename,zipFileName,fileCode)
	
	botoObj = {
	  "FunctionName":funName,
	  "Runtime":runTime,
	  "Role":role,
	  "Handler":handler,
	  "ZipFile":zipped_code,
	  "Timeout":300
	  }

	response = createLamdaFunction(botoObj)

	print(response)

	if ltype == 'lambda_invoke':
		lambdaInvoke(funName,event)


	return render_template('index.html')

def createLamdaFunction(botoObj):
	#print(botoObj)
	try:
		response = lambda_client.create_function(
		  FunctionName=botoObj['FunctionName'],
		  Runtime=botoObj['Runtime'],
		  Role=botoObj['Role'],
		  Handler=botoObj['Handler'],
		  Code=dict(ZipFile=botoObj['ZipFile']),
		  Timeout=botoObj['Timeout']
		)
		#print(response)
	except:
  		print ("lamdbaError==")
  		raise ResourceConflictException('An error occurred (ResourceConflictException) when calling the CreateFunction operation: Function already exist' + botoObj['FunctionName'])
	else:
		print ("LAMBDA CREATED SUCCESSFULLY!!")
		return response

def lambdaInvoke(funName,event):
	res=lambda_client.invoke(
	    FunctionName=funName,
	    InvocationType='Event',
	    LogType='Tail',
	    Payload=event
	)
	print ("LAMBDA INVOKE RESPONSE..")
	print (res)


def fileProcess(filename,zipFileName,fileCode):
	
	# # make zip file of the folder
	# # os.makedirs(os.path.dirname(filename), exist_ok=True)	
	# with open(filename, "w") as f: f.write(fileCode)

	# zf = zipfile.ZipFile(zipFileName, mode='w')
	# try:
	#     #print ('adding README.txt')
	#     zf.write(filename)
	# finally:
	#     #print ('closing')
	#     zf.close()

	# map with boto3 object to create lambda function

	iam_client = boto3.client('iam')
	lambda_client = boto3.client('lambda')
	env_variables = dict() # Environment Variables
	with open(fileCode, 'rb') as f:
	  zipped_code = f.read()
	#print(zipped_code)

	return zipped_code




if __name__ == '__main__':
   app.run(debug = True)