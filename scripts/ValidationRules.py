import pymel.core

# Main register function for validation logic
def get_validation_rules(configuration):
    rules = []
    rules.append(NameRule(configuration))
    rules.append(UVSetRule(configuration))
    return rules

# Validation Status Data Class
# it tells what current status, is test passed and etc.
class ValidationRuleStatus():
	def __init__(self, status_msg, is_passed):
		self.status_msg = status_msg
		self.is_passed = is_passed

# Names Validation Rule
class NameRule():
	def __init__(self, config):
		self.NAME = "Name Status"
		self.set_configuration(config)
	
	def set_configuration(self, config):
		self.__names = config
		
	def apply_rule(self, object_name):
		if object_name not in self.__names:
			return ValidationRuleStatus("Wrong Name", False)
		return ValidationRuleStatus("Ok", True)

# UV Set Validation Rules
class UVSetRule():
	def __init__(self, config):
		self.NAME = "UVSets Status"
		self.set_configuration(config)
	
	def set_configuration(self, config):
		self.__settings = config
	
	def apply_rule(self, maya_object):
		return ValidationRuleStatus("To Much UV Sets", False)
