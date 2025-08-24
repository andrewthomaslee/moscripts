import pytest
from unittest.mock import Mock, patch
import subprocess
from pathlib import Path
import sys
import os  # Import the 'os' module
from moscripts.gum import gum_choose, gum_confirm, GUM
from typer import Exit  # Import Exit from typer


class TestGumConfirm:
    """Test suite for gum_confirm function"""

    def test_gum_confirm_yes(self):
        """Test successful confirmation (user selects Yes)"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0  # gum confirm returns 0 for yes
            mock_run.return_value = mock_result

            result = gum_confirm("Are you sure?")
            assert result is True
            mock_run.assert_called_once_with(
                [str(GUM), "confirm", "Are you sure?"],
                stdin=sys.stdin,
                stdout=subprocess.PIPE,
                stderr=sys.stderr,
                text=True,
                check=False,
            )

    def test_gum_confirm_no(self):
        """Test unsuccessful confirmation (user selects No)"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # gum confirm returns 1 for no
            mock_run.return_value = mock_result

            result = gum_confirm("Are you sure?")
            assert result is False
            mock_run.assert_called_once_with(
                [str(GUM), "confirm", "Are you sure?"],
                stdin=sys.stdin,
                stdout=subprocess.PIPE,
                stderr=sys.stderr,
                text=True,
                check=False,
            )

    def test_gum_confirm_cancellation(self):
        """Test when user cancels (Ctrl+C)"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 130  # Simulate SIGINT
            mock_run.return_value = mock_result

            with pytest.raises(Exit):
                gum_confirm("Are you sure?")
            mock_run.assert_called_once()

    def test_gum_confirm_keyboard_interrupt(self):
        """Test KeyboardInterrupt handling"""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()  # Simulate KeyboardInterrupt
            with pytest.raises(
                KeyboardInterrupt
            ):  # Expect KeyboardInterrupt to be re-raised
                gum_confirm("Are you sure?")
            mock_run.assert_called_once()

    def test_gum_confirm_subprocess_error(self):
        """Test handling of subprocess execution errors"""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, ["gum", "confirm"])
            with pytest.raises(
                subprocess.CalledProcessError
            ):  # Expect CalledProcessError to be re-raised
                gum_confirm("Are you sure?")
            mock_run.assert_called_once()

    def test_gum_confirm_file_not_found(self):
        """Test behavior when gum binary is missing"""
        with patch("moscripts.gum.GUM", Path("/nonexistent/gum")):
            with patch("subprocess.Popen") as mock_popen:
                mock_popen.side_effect = FileNotFoundError("gum: command not found")
                with pytest.raises(
                    FileNotFoundError
                ):  # Expect FileNotFoundError to be re-raised
                    gum_confirm("Are you sure?")
                mock_popen.assert_called_once()


class TestGumChoose:
    """Test suite for gum_choose function"""

    # Test data
    SAMPLE_CHOICES = ["option1", "option2", "option3"]
    EMPTY_CHOICES = []

    def test_gum_choose_basic_success(self):
        """Test successful choice selection"""
        with patch("subprocess.run") as mock_run:
            # Mock successful gum execution
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "option2\n"
            mock_run.return_value = mock_result

            result = gum_choose(self.SAMPLE_CHOICES)

            assert result == "option2"
            mock_run.assert_called_once()

    def test_gum_choose_empty_choices(self):
        """Test behavior with empty choices list"""
        with pytest.raises(ValueError, match="No choices provided."):
            gum_choose(self.EMPTY_CHOICES)

    def test_gum_choose_user_cancellation(self):
        """Test when user cancels (Ctrl+C or ESC)"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 130  # SIGINT
            mock_run.return_value = mock_result

            with pytest.raises(Exit):
                gum_choose(TestGumChoose.SAMPLE_CHOICES)
            mock_run.assert_called_once()

    def test_gum_choose_custom_parameters(self):
        """Test with custom parameters"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "choice\n"
            mock_run.return_value = mock_result

            gum_choose(
                choices=["a", "b"],
                header="Select option:",
                cursor="→ ",
                height=5,
                limit=1,
            )

            # Verify command construction
            expected_cmd = [
                str(GUM),
                "choose",
                "--header",
                "Select option:",
                "--cursor",
                "→ ",
                "--height",
                "5",
                "--limit",
                "1",
                "a",
                "b",
            ]
            mock_run.assert_called_with(
                expected_cmd,
                stdin=sys.stdin,
                stdout=subprocess.PIPE,
                stderr=sys.stderr,
                text=True,
                check=False,
            )

    def test_gum_choose_keyboard_interrupt(self):
        """Test KeyboardInterrupt handling"""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()

            with pytest.raises(
                KeyboardInterrupt
            ):  # Expect KeyboardInterrupt to be re-raised
                gum_choose(TestGumChoose.SAMPLE_CHOICES)
            mock_run.assert_called_once()

    def test_gum_choose_whitespace_stripping(self):
        """Test that whitespace is properly stripped from output"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "  choice with spaces  \n"
            mock_run.return_value = mock_result

            result = gum_choose(["test"])
            assert result == "choice with spaces"

    @pytest.mark.parametrize(
        "choices,expected",
        [
            (["a"], "a"),
            (["x", "y", "z"], "y"),
            (["single"], "single"),
        ],
    )
    def test_gum_choose_parametrized(self, choices, expected):
        """Parametrized testing for various choice combinations"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = f"{expected}\n"
            mock_run.return_value = mock_result

            result = gum_choose(choices)
            assert result == expected


class TestGumChooseIntegration:
    """Integration tests with actual gum binary (optional)"""

    def test_gum_binary_exists(self):
        """Verify gum binary is accessible"""
        assert GUM.exists()
        assert GUM.is_file()
        assert os.access(GUM, os.X_OK)


class TestGumChooseErrorHandling:
    """Test error handling and edge cases"""

    def test_gum_choose_subprocess_error(self):
        """Test handling of subprocess execution errors (e.g., timeout)"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # Simulate a non-zero exit code for error
            mock_result.stdout = ""
            mock_result.stderr = "Error: command timed out\n"
            mock_run.return_value = mock_result

            with pytest.raises(Exit):  # Expect Exit to be raised
                gum_choose(TestGumChoose.SAMPLE_CHOICES)
            mock_run.assert_called_once()

    def test_gum_choose_file_not_found(self):
        """Test behavior when gum binary is missing"""
        with patch("moscripts.gum.GUM", Path("/nonexistent/gum")):
            with patch("subprocess.Popen") as mock_popen:  # Patch Popen directly
                # Configure mock_popen to raise FileNotFoundError when instantiated
                mock_popen.side_effect = FileNotFoundError("gum: command not found")

                with pytest.raises(
                    FileNotFoundError
                ):  # Expect FileNotFoundError to be re-raised
                    gum_choose(TestGumChoose.SAMPLE_CHOICES)
                mock_popen.assert_called_once()


# Fixtures for common test setup
@pytest.fixture
def mock_subprocess_run():
    """Fixture for mocking subprocess.run"""
    with patch("subprocess.run") as mock:
        yield mock


@pytest.fixture
def successful_gum_result():
    """Fixture providing successful gum execution mock"""
    mock = Mock()
    mock.returncode = 0
    mock.stdout = "selected_option\n"
    return mock


@pytest.fixture
def cancelled_gum_result():
    """Fixture providing cancelled gum execution mock"""
    mock = Mock()
    mock.returncode = 1
    mock.stdout = ""
    return mock


# Example usage in individual tests
def test_gum_choose_with_fixtures(mock_subprocess_run, successful_gum_result):
    """Example test using fixtures"""
    mock_subprocess_run.return_value = successful_gum_result

    result = gum_choose(["test1", "test2"])
    assert result == "selected_option"


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line(
        "markers", "interactive: mark test as requiring user interaction"
    )
