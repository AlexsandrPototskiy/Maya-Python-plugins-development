# Validation Status Data Class
# it tells what current status, is test passed and etc.
class ValidationRuleStatus():
	def __init__(self, status_msg, is_passed):
		self.status_msg = status_msg
		self.is_passed = is_passed

# base validation rule		
class ValidationRule(object):
	NAME = "Abstract Rule"

    def set_configuration(self, config):
        raise NotImplementedError('[ValidationRule Module] subclass should overrride set_configuration function')

	def apply_rule(self, object_for_validation):
		raise NotImplementedError('[ValidationRule Module] subclass should overrride apply_rule function')

# names validation
class NameRule(ValidationRule):
	
	def __init__(self, config):
		super(NameRule, self).__init__()
		self.NAME = "Name Status"
		self.set_configuration(config)
	
	def set_configuration(self, config):
		self.__names = names_from_configuration
		
	def apply_rule(self, object_name):
		if object_name not in self.__names:
			return ValidationRuleStatus("Wrong Name", False)
		return ValidationRuleStatus("Ok", True)


