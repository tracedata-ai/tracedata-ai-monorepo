import pytest

# Use this to set up the testing "ground rules" that the agent must follow for every feature.
@pytest.fixture(scope="session")
def setup_environment():
    print("Setting up test environment for TraceData.ai")
    yield
    print("Tearing down test environment")
