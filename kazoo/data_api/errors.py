
class DataApiErrors():

	# ZOOKEEPER
	ZOOKEEPER_ERROR = "Zookeeper could not process the data"
	ZOOKEEPER_UNAVAILABLE = "Connection to Zookeeper has been lost"

	# PARAMETERS
	PARAMETER_TYPE = "Wrong parameter type"
	PARAMETER_MISSING = "Missing or None parameter"
	CLASSIFICATION_VALUE = "Invalid character in classification string"
	CLASSIFICATION_LENGTH = "Invalid length for classification string"

	# SECURITY
	PASSWORD_MISMATCH = "Password does not match"
	VERSION_MISMATCH = "Version of the data does not match"
	LOCK_TIMEOUT = "Lock on zNode could not be acquired"
	
	
class DataApiException(Exception):
	pass
