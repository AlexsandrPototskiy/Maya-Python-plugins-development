# do not delete this imports it is importante for Custom Validation Rules
from base_abstract_rule import BaseAbstractRule
from validator_data_classes import ValidationRuleStatus


# inherite your rule from this abstract class
class CustomAbstractRule(BaseAbstractRule):
	NAME = "Abstract Rule"

	# function MUST be ovverriden
	def __init__(self):
		raise NotImplementedError("[AssetValidator] you must inherite from this class")

	# class must return ValidationRuleStatus data class
	# function MUST be ovverriden
	def apply_rule(self, maya_object):
		raise NotImplementedError("[AssetValidator] abstract function must be ovveriden before use")


# function must return list of classes derrived form CustomAbstractRule 
def register_custom_rules():
	rules = []
	# implement your validation rule and add it to list
	rules.append(TestCustomRule())
	return rules


# example implementation
class TestCustomRule(CustomAbstractRule):
	NAME = "Test Rule"

	def __init__(self):
		pass

	def apply_rule(self, maya_object):
		return ValidationRuleStatus("Test Passed", True)

