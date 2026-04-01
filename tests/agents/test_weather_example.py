"""Test suite for Phase 1 PoC agent implementation."""

import json
import pytest


class TestLLMAdapterFactory:
    """Test LLM adapter factory pattern."""

    def test_load_openai_model(self):
        """Test loading OpenAI model via factory."""
        from common.llm import load_llm, OpenAIModel

        # This will fail without OPENAI_API_KEY, which is expected
        # In CI/real env, the key should be set
        try:
            config = load_llm(OpenAIModel.GPT_4O)
            assert config.provider == "openai"
            assert config.model == "gpt-4o"
            assert config.adapter is not None
        except EnvironmentError as e:
            if "OPENAI_API_KEY" in str(e):
                pytest.skip("OPENAI_API_KEY not set in environment")
            raise

    def test_load_anthropic_model(self):
        """Test loading Anthropic model via factory."""
        from common.llm import load_llm, AnthropicModel

        try:
            config = load_llm(AnthropicModel.CLAUDE_35_SONNET_20241022)
            assert config.provider == "anthropic"
            assert config.model == "claude-3-5-sonnet-20241022"
            assert config.adapter is not None
        except EnvironmentError as e:
            if "ANTHROPIC_API_KEY" in str(e):
                pytest.skip("ANTHROPIC_API_KEY not set in environment")
            raise


class TestWeatherTrafficTools:
    """Test weather and traffic tools."""

    def test_weather_tool(self):
        """Test weather tool returns formatted string."""
        from agents.tools.weather_traffic import get_weather

        # get_weather is a StructuredTool, call invoke method
        result = get_weather.invoke({"location": "Singapore"})
        assert isinstance(result, str)
        assert "singapore" in result.lower()
        assert "Weather" in result

    def test_traffic_tool(self):
        """Test traffic tool returns formatted string."""
        from agents.tools.weather_traffic import get_traffic

        # get_traffic is a StructuredTool, call invoke method
        result = get_traffic.invoke({"location": "Malaysia"})
        assert isinstance(result, str)
        assert "malaysia" in result.lower()
        assert "Traffic" in result

    def test_tools_with_unknown_location(self):
        """Test tools handle unknown locations gracefully."""
        from agents.tools.weather_traffic import get_weather, get_traffic

        weather_result = get_weather.invoke({"location": "UnknownCity"})
        traffic_result = get_traffic.invoke({"location": "UnknownCity"})

        assert "Unknown location" in weather_result
        assert "Unknown location" in traffic_result


class TestSystemPrompts:
    """Test system prompts configuration."""

    def test_all_prompts_exist(self):
        """Test that all expected prompts are defined."""
        from common.config.system_prompts import SYSTEM_PROMPTS, PromptType

        # Verify all PromptType enum values have corresponding prompts
        for prompt_type in PromptType:
            assert prompt_type in SYSTEM_PROMPTS
            assert SYSTEM_PROMPTS[prompt_type]
            assert isinstance(SYSTEM_PROMPTS[prompt_type], str)
            assert len(SYSTEM_PROMPTS[prompt_type]) > 0

    def test_get_prompt_function(self):
        """Test get_prompt helper function."""
        from common.config.system_prompts import get_prompt, PromptType

        prompt = get_prompt(PromptType.WEATHER_TRAFFIC)
        assert isinstance(prompt, str)
        assert "Weather" in prompt
        assert "Traffic" in prompt

    def test_prompt_key_lookup(self):
        """Test prompt lookup by string key."""
        from common.config.system_prompts import get_prompt

        prompt = get_prompt("weather_traffic")
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestAgentABC:
    """Test Agent ABC base class."""

    def test_agent_initialization(self):
        """Test agent initialization with mock LLM."""
        from unittest.mock import Mock

        from agents.base.agent import Agent
        from agents.tools import get_weather

        mock_llm = Mock()
        agent = Agent(
            llm=mock_llm,
            agent_name="TestAgent",
            tools=[get_weather],
            system_prompt="Test prompt",
        )

        assert agent.agent_name == "TestAgent"
        assert len(agent.tools) == 1
        assert agent._graph is None  # Lazy initialization

    def test_agent_repr(self):
        """Test agent __repr__ method."""
        from unittest.mock import Mock

        from agents.base.agent import Agent
        from agents.tools import get_weather

        mock_llm = Mock()
        agent = Agent(
            llm=mock_llm,
            agent_name="TestAgent",
            tools=[get_weather],
            system_prompt="Test prompt",
        )

        repr_str = repr(agent)
        assert "TestAgent" in repr_str
        assert "tools=1" in repr_str


class TestWeatherTrafficAgentExample:
    """Test WeatherTrafficAgent example."""

    def test_agent_initialization(self):
        """Test WeatherTrafficAgent initializes with correct tools."""
        from unittest.mock import Mock

        from agents.examples import WeatherTrafficAgent

        mock_llm = Mock()
        agent = WeatherTrafficAgent(llm=mock_llm)

        assert agent.agent_name == "WeatherTrafficAgent"
        assert len(agent.tools) == 2  # weather + traffic
        assert agent.tools[0].name == "get_weather"
        assert agent.tools[1].name == "get_traffic"

    def test_agent_has_system_prompt(self):
        """Test WeatherTrafficAgent has system prompt."""
        from unittest.mock import Mock

        from agents.examples import WeatherTrafficAgent

        mock_llm = Mock()
        agent = WeatherTrafficAgent(llm=mock_llm)

        assert agent.system_prompt
        assert isinstance(agent.system_prompt, str)
        assert "Weather" in agent.system_prompt
        assert "Traffic" in agent.system_prompt


class TestAgentInvocation:
    """Test agent invocation (with mock LLM)."""

    def test_agent_string_representation(self):
        """Test agent __str__ shows agent details."""
        from unittest.mock import Mock

        from agents.examples import WeatherTrafficAgent

        mock_llm = Mock()
        mock_llm.__class__.__name__ = "MockChatModel"

        agent = WeatherTrafficAgent(llm=mock_llm)
        str_repr = str(agent)

        assert "WeatherTrafficAgent" in str_repr
        assert "get_weather" in str_repr
        assert "get_traffic" in str_repr
        assert "MockChatModel" in str_repr


class TestIntegration:
    """Integration tests for Phase 1 PoC."""

    def test_agent_adapter_integration(self):
        """Test agent can be created with adapter-provided LLM.

        This test validates the integration path:
        load_llm() -> LLMConfig -> adapter.get_chat_model() -> Agent init
        """
        from unittest.mock import Mock, patch
        import os

        # Set API key in environment
        os.environ["OPENAI_API_KEY"] = "test-key"

        # Mock the actual LLM model to avoid API calls
        with patch("langchain_openai.ChatOpenAI") as mock_chat:
            mock_llm_instance = Mock()
            mock_chat.return_value = mock_llm_instance

            from common.llm import load_llm, OpenAIModel
            from agents.examples import WeatherTrafficAgent

            config = load_llm(OpenAIModel.GPT_4O)
            llm = config.adapter.get_chat_model()

            agent = WeatherTrafficAgent(llm=llm)

            assert agent.llm == mock_llm_instance
            assert agent.agent_name == "WeatherTrafficAgent"
            assert len(agent.tools) == 2
