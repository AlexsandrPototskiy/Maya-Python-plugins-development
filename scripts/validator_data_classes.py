# Validation Status Data Class
# it tells what current status, is test passed and etc.
class ValidationRuleStatus():

    def __init__(self, status_msg, is_passed):
        self.status_msg = status_msg
        self.is_passed = is_passed