"""
Shared test fixtures for adversarial-workflow tests.

This module provides common fixtures used across all test modules,
including temporary directories, sample files, and mocked dependencies.
"""

import tempfile
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory with basic structure."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create basic project structure
    (project_dir / ".adversarial").mkdir()
    (project_dir / ".adversarial" / "logs").mkdir()
    
    # Create a basic config file
    config_content = """
project_name: test_project
openai_api_key: sk-fake-test-key
aider_model: gpt-4o
stages:
  - plan_evaluation
  - implementation
  - code_review
  - test_validation
"""
    (project_dir / ".adversarial" / "config.yaml").write_text(config_content.strip())
    
    # Create a basic .env file
    env_content = "OPENAI_API_KEY=sk-fake-test-key\n"
    (project_dir / ".env").write_text(env_content)
    
    return project_dir


@pytest.fixture
def sample_task_content():
    """Sample task file content for testing."""
    return """# TEST-001: Sample Test Task

**Status**: Todo
**Priority**: Medium
**Assigned To**: test-agent
**Estimated Effort**: 1 hour

## Overview

This is a sample task for testing the adversarial workflow system.

## Requirements

### Functional Requirements
1. Implement a simple function
2. Add basic error handling
3. Include unit tests

### Non-Functional Requirements
- Performance: Function should complete in <100ms
- Maintainability: Clear documentation

## Implementation Plan

### Files to Create
1. `src/test_function.py` - Main implementation
2. `tests/test_test_function.py` - Unit tests

### Approach
Simple implementation with proper error handling.

## Acceptance Criteria

- Function works correctly
- Tests pass
- Documentation is clear

## Success Metrics

- All tests pass
- Code coverage >80%
"""


@pytest.fixture
def sample_task_file(tmp_project, sample_task_content):
    """Create a sample task file in the test project."""
    task_file = tmp_project / "test_task.md"
    task_file.write_text(sample_task_content)
    return task_file


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run calls to avoid running actual aider commands."""
    with patch('subprocess.run') as mock_run:
        # Default successful aider run
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Aider completed successfully",
            stderr=""
        )
        yield mock_run


@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API calls to avoid actual API requests during tests."""
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="Test response from mocked OpenAI"
                    )
                )
            ]
        )
        yield mock_create


@pytest.fixture
def sample_config():
    """Sample configuration dictionary for testing."""
    return {
        'project_name': 'test_project',
        'openai_api_key': 'sk-fake-test-key',
        'aider_model': 'gpt-4o',
        'stages': [
            'plan_evaluation',
            'implementation', 
            'code_review',
            'test_validation'
        ],
        'working_directory': '/tmp/test',
        'output_directory': '.adversarial/logs'
    }


@pytest.fixture
def mock_file_operations():
    """Mock file system operations for isolated testing."""
    mocks = {}
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.is_file') as mock_is_file, \
         patch('pathlib.Path.is_dir') as mock_is_dir:
        
        # Default to files/dirs existing
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_is_dir.return_value = True
        
        mocks['exists'] = mock_exists
        mocks['is_file'] = mock_is_file
        mocks['is_dir'] = mock_is_dir
        
        yield mocks


@pytest.fixture(autouse=True)
def change_test_dir(tmp_project):
    """Change to temporary directory for each test to avoid side effects."""
    old_cwd = os.getcwd()
    os.chdir(tmp_project)
    yield
    os.chdir(old_cwd)


@pytest.fixture
def mock_aider_command():
    """Mock aider command execution with realistic outputs."""
    def _mock_aider(command_type='evaluate'):
        """Create a mock aider command result based on type."""
        if command_type == 'evaluate':
            return Mock(
                returncode=0,
                stdout="""
# ADV-TEST-PLAN-EVALUATION

## Summary
Plan evaluation completed successfully.

## Findings
- Task specification is clear
- Implementation approach is sound
- Estimated effort is reasonable

## Recommendations
- Proceed with implementation
- Add error handling for edge cases
- Include comprehensive tests

## Token Usage
- Input tokens: 1500
- Output tokens: 500
- Total tokens: 2000
""",
                stderr=""
            )
        elif command_type == 'implement':
            return Mock(
                returncode=0,
                stdout="Implementation completed successfully",
                stderr=""
            )
        else:
            return Mock(
                returncode=0,
                stdout=f"{command_type} completed successfully",
                stderr=""
            )
    
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = lambda *args, **kwargs: _mock_aider()
        yield _mock_aider