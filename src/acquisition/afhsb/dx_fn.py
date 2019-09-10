
# A self-defined diagnosis-classification function takes in 
# a list of icd codes and returns a category. 
# Look at dx2ili and dx2flu for reference.

def get_flu_cat(dx):
	# flu1 (influenza)
	if (len(dx) == 0): return None
	dx = dx.capitalize()
	if (dx.isnumeric()):
		for prefix in ["487", "488"]:
			if (dx.startswith(prefix)): return 1
		for i in range(0, 7):
			prefix = str(480 + i)
			if (dx.startswith(prefix)): return 2
		for i in range(0, 7):
			prefix = str(460 + i)
			if (dx.startswith(prefix)): return 3
		for prefix in ["07999", "3829", "7806", "7862"]:
			if (dx.startswith(prefix)): return 3
	elif (dx[0].isalpha() and dx[1:].isnumeric()):
		for prefix in ["J09", "J10", "J11"]:
			if (dx.startswith(prefix)): return 1
		for i in range(12, 19):
			prefix = "J{}".format(i)
			if (dx.startswith(prefix)): return 2
		for i in range(0, 7):
			prefix = "J0{}".format(i)
			if (dx.startswith(prefix)): return 3
		for i in range(20, 23):
			prefix = "J{}".format(i)
			if (dx.startswith(prefix)): return 3
		for prefix in ["J40", "R05", "H669", "R509", "B9789"]:
			if (dx.startswith(prefix)): return 3
	else:
		return None

def dx2flu(dx_list):
	for dx in dx_list:
		flu_cat = get_flu_cat(dx)
		if (flu_cat != None): return flu_cat
	return 0

def dx2ili(dx_list, get_field):
	is_fever, respiratory = False, False
	for dx in dx_list:
		if (len(dx) == 0): continue
		dx = dx.capitalize()
		# ICD-9
		if (dx.isnumeric()):
			# direct mention of influenza: 487-488
			if (dx.startswith("487") or dx.startswith("488")): return True
			# febrile viral illness: 079.99
			if (dx.startswith("07999")): return True
			# fever (780.6) combined with a respiratory symptom (462 or 786.2)
			if (dx.startswith("7806")): 
				is_fever = True
				if (respiratory): return True
			if (dx.startswith("462") or dx.startswith("7862")): 
				respiratory = True
				if (is_fever): return True
		# ICD-10 (using approximate conversions between ICD-9-CM and ICD-10-CM from https://www.icd10data.com/Convert/)
		else:
			# direct mention of influenza: 
			if (dx.startswith("J1100") or dx.startswith("J129") or dx.startswith("J111")
				or dx.startswith("J112") or dx.startswith("J1181") or dx.startswith("J1189")):
				return True
			if (dx.startswith("J09X") or dx.startswith("J1008") or dx.startswith("J101")):
				return True
			# febrile viral illness: B97.89
			if (dx.startswith("B9789")): return True
			# fever: R50(R50.2, R50.9, R50.81, R50.82, R50.83, R50.84), R68.83, R68.O, 
			if (dx.startswith("R50") or dx.startswith("R6883") or dx.startswith("R680")):
				is_fever = True
				if (respiratory): return True
			# a respiratory sympton: J02.9, R05
			if (dx.startswith("J029") or dx.startswith("R05")):
				respiratory = True
				if (is_fever): return True

	return False

DXFN_DICT = {'ili': dx2ili, 'flucat': dx2flu}