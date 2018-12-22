"""
Apache Test Fixture

This fixture doesn't do any setup, but verifies that the created service is
running default apache.
"""
import requests
from cloudless.testutils.blueprint_tester import call_with_retries
from cloudless.testutils.fixture import BlueprintTestInterface, SetupInfo
from cloudless.types.networking import CidrBlock

RETRY_DELAY = float(10.0)
RETRY_COUNT = int(6)

class BlueprintTest(BlueprintTestInterface):
    """
    Fixture class that creates the dependent resources.
    """
    def setup_before_tested_service(self, network):
        """
        Create the dependent services needed to test this service.
        """
        # Since this service has no dependencies, do nothing.
        return SetupInfo({}, {})

    def setup_after_tested_service(self, network, service, setup_info):
        """
        Do any setup that must happen after the service under test has been
        created.
        """
        my_ip = requests.get("http://ipinfo.io/ip")
        test_machine = CidrBlock(my_ip.content.decode("utf-8").strip())
        self.client.paths.add(test_machine, service, 9090)

    def verify(self, network, service, setup_info):
        """
        Given the network name and the service name of the service under test,
        verify that it's behaving as expected.
        """
        def check_prometheus():
            instances = self.client.service.get_instances(service)
            assert instances, "No instances found!"
            for instance in instances:
                endpoint = 'http://%s:9090/api/v1/query' % instance.public_ip
                params = {"query": "prometheus_build_info"}
                response = requests.get(endpoint, params=params)
                api_response = response.json()
                assert api_response["status"] == "success"
                monitoring_self = False
                for result in api_response["data"]["result"]:
                    if result["metric"]["instance"] == "localhost:9090":
                        monitoring_self = True
                assert monitoring_self, "Found no metrics for Prometheus"
        call_with_retries(check_prometheus, RETRY_COUNT, RETRY_DELAY)
