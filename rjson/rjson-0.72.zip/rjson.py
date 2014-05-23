import json

openChar = "{"

def parseJson(input):
	if input == None or type(input) is not str:
		# no exception, just returning nothing
		return

	startIndex = -1

	for i in range(0, len(input)):
		char = input[i]
		if startIndex == -1 and char == openChar:
			startIndex = i
			continue

		try:
			jsonObj = json.loads(input[startIndex:i+1])
			startIndex = -1
			yield jsonObj
		except ValueError, e:
			# not the best, but most practical for now
			continue