from robot.libraries.BuiltIn import BuiltIn
from pabot import PabotLib

class server_distributor:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.pabotlib = PabotLib()

    def start_suite(self, name, attr):
        self.server = self.get_server()
        BuiltIn().set_suite_variable("${url}", self.server)

    def end_suite(self, name, attr):
        self.release_server()

    def get_server(self):
        try:
            self.set_name = self.pabotlib.acquire_value_set("server")
        except ValueError:
            assert self.set_name != None
        finally:
            return self.pabotlib.get_value_from_set("url")

    def release_server(self):
        self.pabotlib.release_value_set()