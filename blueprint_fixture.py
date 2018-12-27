"""
Apache Test Fixture

This fixture doesn't do any setup, but verifies that the created service is
running default apache.
"""
import requests
from cloudless.testutils.blueprint_tester import call_with_retries
from cloudless.testutils.fixture import BlueprintTestInterface, SetupInfo
from cloudless.types.networking import CidrBlock

SERVICE_BLUEPRINT = os.path.join(os.path.dirname(__file__), "example-postgres/blueprint.yml")

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
        # Create postgres so we can test Prometheus with remote storage
        service_name = "postgres"
        service = self.client.service.create(network, service_name, SERVICE_BLUEPRINT, count=1)

        # Set the postgres_url to the IP of the first postgres instance
        blueprint_variables = {
            "postgres_url": [i.private_ip for s in service.subnetworks for i in s.instances][0]
            }

        return SetupInfo(
            {"service_name": service_name},
            blueprint_variables)

    def setup_after_tested_service(self, network, service, setup_info):
        """
        Do any setup that must happen after the service under test has been
        created.
        """
        # Make sure we can connect to Prometheus
        my_ip = requests.get("http://ipinfo.io/ip")
        test_machine = CidrBlock(my_ip.content.decode("utf-8").strip())
        self.client.paths.add(test_machine, service, 9090)

        # Add this last because we want to make sure that our service can handle a delay before
        # getting connectivity to postgres.
        postgres_service_name = setup_info.deployment_info["service_name"]
        postgres_service = self.client.service.get(network, postgres_service_name)
        self.client.paths.add(service, consul_service, 5432)

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
