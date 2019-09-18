
# A self-defined diagnosis-classification function takes in 
# a list of icd codes and returns a category. 
# Look at dx2ili and dx2flu for reference.

def get_flu_cat(dx):
	"""Get the narrowest flu categorization for a single dx code.

	Args:
		dx (:obj:`str`): Diagnosis code

	Returns:
		int, optional:
		* 1, if code is in single-code flu1 (and thus also flu2 and flu3) set
		* 2, if code is in single-code flu2-flu1 (and thus also flu3) set
		* 3, if code is in single-code flu3-flu2 set
		* None, if code does not fall in single-code flu3 set
	"""
	if (len(dx) == 0): return None
	dx = dx.capitalize()
	if (dx.isnumeric()):
		# flu1 (influenza) code:
		for prefix in ["487", "488"]:
			if (dx.startswith(prefix)): return 1
		# flu2 (P&I) code not already above:
		for i in range(0, 7):
			prefix = str(480 + i) # "480".."486" (487 & 488 already above)
			if (dx.startswith(prefix)): return 2
		# flu3 (P&I&ILI&ARI, using one version of AFHSB ILI codeset) code not
		# already above:
		for i in range(0, 7):
			prefix = str(460 + i) # "460".."466"
			if (dx.startswith(prefix)): return 3
		for prefix in ["07999", "3829", "7806", "7862"]:
			if (dx.startswith(prefix)): return 3
	elif (dx[0].isalpha() and dx[1:].isnumeric()):
		# flu1 (influenza) code:
		for prefix in ["J09", "J10", "J11"]:
			if (dx.startswith(prefix)): return 1
		# flu2 (P&I) code not already above:
		for i in range(12, 19):
			prefix = "J{}".format(i) # "J12".."J18"
			if (dx.startswith(prefix)): return 2
		# flu3 (P&I&ILI&ARI, using one version of AFHSB ILI codeset) code not
		# already above:
		for i in range(0, 7):
			prefix = "J0{}".format(i) # "J00".."J06"
			if (dx.startswith(prefix)): return 3
		for i in range(20, 23):
			prefix = "J{}".format(i) # "J20".."J22"
			if (dx.startswith(prefix)): return 3
		for prefix in ["J40", "R05", "H669", "R509", "B9789"]:
			if (dx.startswith(prefix)): return 3
	else:
		return None

def dx2flu(dx_list):
	"""Get the narrowest any-listed flu categorization for a dx_list.

	Args:
		dx_list (:obj:`list` of :obj:`str`): List of diagnosis codes

	Returns:
		int:
		* 1, if list is in any-listed-flu1
		* 2, if list is in any-listed-flu2 minus any-listed-flu1
		* 3, if list is in any-listed-flu3 minus any-listed-flu2
		* 0, if list does not fall in any-listed-flu3
	"""
	narrowest_flu_cat = 4
	for dx in dx_list:
		flu_cat = get_flu_cat(dx)
		if (flu_cat):
			narrowest_flu_cat = min(narrowest_flu_cat, flu_cat)
	if narrowest_flu_cat == 4:
		return 0
	else:
		return narrowest_flu_cat

def dx2ili(dx_list):
	"""Check whether diagnosis code list fulfills Charu et al. 2017 ILI criteria.

	Args:
		dx_list (:obj:`list` of :obj:`str`): List of diagnosis codes

	Returns:
		bool: whether `dx_list` fulfills Charu et al. 2017 ILI criteria.

		For ICD-9 records, directly uses criteria from the paper:
			Charu, Vivek, Scott Zeger, Julia Gog, Ottar N. Bjørnstad, Stephen
			Kissler, Lone Simonsen, Bryan T. Grenfell, and Cécile Viboud.
			"Human mobility and the spatial transmission of influenza in the
			United States." PLoS Computational Biology 13, no. 2 (2017):
			e1005382; Available at
			<https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005382>.
		For ICD-10 records, we mapped the ICD-9 specification to ICD-10, using
		<https://www.icd10data.com/Convert/> and other ICD-10 information from
		<https://www.icd10data.com/>.
	"""
	# Maintain flags for whether previous dx codes in the list qualified as
	# fever or respiratory illness:
	is_fever, respiratory = False, False
	for dx in dx_list:
		if (len(dx) == 0): continue
		dx = dx.capitalize()
		# ICD-9
		if (dx.isnumeric()):
			# direct mention of influenza: 487-488
			if (dx.startswith("487") or dx.startswith("488")): return True
			# febrile viral illness: 079.99 (/ unspecified viral infection)
			if (dx.startswith("07999")): return True
			# fever (780.6; actually includes other physiologic disturbances of temperature regulation) combined with a respiratory symptom (462 or 786.2)
			if (dx.startswith("7806")): 
				is_fever = True
				if (respiratory): return True
			if (dx.startswith("462") or dx.startswith("7862")): 
				respiratory = True
				if (is_fever): return True
		# ICD-10 (using approximate conversions between ICD-9-CM and ICD-10-CM from https://www.icd10data.com/Convert/)
		else:
			# direct mention of influenza: chapters J09--J11
			if (dx.startswith("J09") or dx.startswith("J10") or dx.startswith("J11")):
				return True
			# febrile viral illness / mapping from 079.99: B97.89
			if (dx.startswith("B9789")): return True
			# fever: R50 (R50.2, R50.9, R50.81, R50.82, R50.83, R50.84), plus other codes converted from 780.6: R68.83, R68.0
			if (dx.startswith("R50") or dx.startswith("R6883") or dx.startswith("R680")):
				is_fever = True
				if (respiratory): return True
			# a respiratory symptom: J02.9, R05
			if (dx.startswith("J029") or dx.startswith("R05")):
				respiratory = True
				if (is_fever): return True

	return False

DXFN_DICT = {'ili': dx2ili, 'flucat': dx2flu}