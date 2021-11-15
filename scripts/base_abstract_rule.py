class BaseAbstractRule(object):
	NAME = "Abstract Rule"

	def __init__(self):
		raise NotImplementedError("[AssetValidator] you must inherite from this class")

	def apply_rule(self, maya_object):
		raise NotImplementedError("[AssetValidator] abstract function must be ovveriden before use")