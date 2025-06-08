#!/usr/bin/env python3
"""
Unit tests for PR tracker core functionality.
Tests the main capabilities without external API calls or file modifications.
"""

import unittest
import tempfile
import csv
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
import re

# Import the modules to test
import collect_data
import generate_chart


class TestPRTracker(unittest.TestCase):
    """Test core PR tracker functionality."""

    def setUp(self):
        """Set up test fixtures with temporary directories."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Sample CSV data for testing
        self.sample_csv_data = [
            ["timestamp", "copilot_total", "copilot_merged", "codex_total", "codex_merged", 
             "cursor_total", "cursor_merged", "devin_total", "devin_merged"],
            ["2025-06-01 10:00:00", "1000", "400", "2000", "1600", "100", "80", "500", "300"],
            ["2025-06-02 10:00:00", "1100", "450", "2100", "1650", "120", "90", "550", "330"],
            ["2025-06-03 10:00:00", "1200", "500", "2200", "1700", "140", "100", "600", "360"]
        ]

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def create_test_csv(self):
        """Create a test CSV file with sample data."""
        csv_file = self.temp_path / "test_data.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.sample_csv_data)
        return csv_file

    def test_core_data_collection_logic(self):
        """Test that data collection logic processes API responses correctly."""
        # Mock GitHub API response
        mock_response = MagicMock()
        mock_response.json.return_value = {"total_count": 42}
        mock_response.raise_for_status.return_value = None
        
        with patch('collect_data.requests.get', return_value=mock_response):
            with patch('collect_data.Path') as mock_path:
                # Mock CSV file operations
                mock_csv_file = MagicMock()
                mock_path.return_value = mock_csv_file
                mock_csv_file.exists.return_value = False
                mock_csv_file.open.return_value.__enter__ = MagicMock()
                mock_csv_file.open.return_value.__exit__ = MagicMock()
                
                # Test data collection
                result = collect_data.collect_data()
                
                # Verify API was called for each query
                self.assertEqual(mock_response.json.call_count, len(collect_data.Q))
                # Verify CSV operations were attempted
                mock_csv_file.open.assert_called()

    def test_readme_update_capability(self):
        """Test README updating capability with mock data."""
        # Create test DataFrame
        df = pd.DataFrame({
            'timestamp': ['2025-06-01 10:00:00'],
            'copilot_total': [1000],
            'copilot_merged': [400],
            'codex_total': [2000], 
            'codex_merged': [1600],
            'cursor_total': [100],
            'cursor_merged': [80],
            'devin_total': [500],
            'devin_merged': [300]
        })
        
        # Create test README content
        readme_content = """# Test README

Some content here.

## Current Statistics

| Project | Total PRs | Merged PRs | Merge Rate |
| ------- | --------- | ---------- | ---------- |
| Copilot | 999 | 399 | 39.94% |

More content here.
"""
        readme_file = self.temp_path / "README.md"
        readme_file.write_text(readme_content)
        
        # Test README update
        with patch('generate_chart.Path') as mock_path:
            mock_path.return_value = readme_file
            result = generate_chart.update_readme(df)
            
            # Verify update was successful
            self.assertTrue(result)
            
            # Check updated content
            updated_content = readme_file.read_text()
            self.assertIn("| Copilot | 1,000 | 400 | 40.00% |", updated_content)
            self.assertIn("| Codex   | 2,000 | 1,600 | 80.00% |", updated_content)
            self.assertIn("| Cursor  | 100 | 80 | 80.00% |", updated_content)
            self.assertIn("| Devin   | 500 | 300 | 60.00% |", updated_content)

    def test_chart_generation_capability(self):
        """Test chart generation processes data correctly."""
        # Create test CSV file
        csv_file = self.create_test_csv()
        
        # Mock the chart generation to avoid creating actual image files
        with patch('generate_chart.plt.subplots') as mock_subplots, \
             patch('generate_chart.plt.tight_layout'), \
             patch('generate_chart.plt.subplots_adjust'), \
             patch('generate_chart.Path') as mock_path, \
             patch('generate_chart.export_chart_data_json') as mock_export, \
             patch('generate_chart.update_readme') as mock_update_readme, \
             patch('generate_chart.update_github_pages') as mock_update_pages:
            
            # Mock the matplotlib figure and axes
            mock_fig = MagicMock()
            mock_ax1 = MagicMock()
            mock_ax2 = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax1)
            mock_ax1.twinx.return_value = mock_ax2
            
            # Mock Path to return a temporary path for chart saving
            mock_chart_path = self.temp_path / "chart.png"
            mock_path.return_value.mkdir = MagicMock()
            mock_path.return_value.__truediv__ = lambda self, other: mock_chart_path
            
            # Test chart generation
            result = generate_chart.generate_chart(csv_file)
            
            # Verify successful generation
            self.assertTrue(result)
            
            # Verify supporting functions were called
            mock_export.assert_called_once()
            mock_update_readme.assert_called_once()
            mock_update_pages.assert_called_once()

    def test_github_pages_update_capability(self):
        """Test GitHub Pages updating capability."""
        # Create test DataFrame
        df = pd.DataFrame({
            'timestamp': ['2025-06-01 10:00:00'],
            'copilot_total': [1000],
            'copilot_merged': [400],
            'codex_total': [2000],
            'codex_merged': [1600], 
            'cursor_total': [100],
            'cursor_merged': [80],
            'devin_total': [500],
            'devin_merged': [300]
        })
        
        # Create test HTML content with placeholder data
        html_content = """<!DOCTYPE html>
<html>
<body>
    <tr data-agent="copilot">
        <td>Copilot</td>
        <td>999</td>
        <td>399</td>
        <td>39.94%</td>
    </tr>
    <span id="last-updated">June 01, 2025 09:00 UTC</span>
</body>
</html>"""
        
        html_file = self.temp_path / "index.html"
        html_file.write_text(html_content)
        
        # Test GitHub Pages update
        with patch('generate_chart.Path') as mock_path:
            mock_path.return_value = html_file
            result = generate_chart.update_github_pages(df)
            
            # Verify update was successful
            self.assertTrue(result)
            
            # Check updated content contains new data
            updated_content = html_file.read_text()
            self.assertIn("1,000", updated_content)  # Updated copilot total
            self.assertIn("400", updated_content)    # Updated copilot merged
            self.assertIn("40.00%", updated_content) # Updated copilot rate

    def test_chart_data_json_export(self):
        """Test JSON export for interactive charts."""
        # Create test DataFrame with percentage columns (as created by generate_chart)
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(['2025-06-01 10:00:00', '2025-06-02 10:00:00']),
            'copilot_total': [1000, 1100],
            'copilot_merged': [400, 450],
            'codex_total': [2000, 2100],
            'codex_merged': [1600, 1650],
            'cursor_total': [100, 120],
            'cursor_merged': [80, 90],
            'devin_total': [500, 550],
            'devin_merged': [300, 330],
            # Add percentage columns that export_chart_data_json expects
            'copilot_percentage': [40.0, 40.9],
            'codex_percentage': [80.0, 78.6],
            'cursor_percentage': [80.0, 75.0],
            'devin_percentage': [60.0, 60.0]
        })
        
        # Create temporary docs directory and JSON file
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir(exist_ok=True)
        json_file = docs_dir / "chart-data.json"
        
        # Test JSON export using actual temp directory
        with patch('generate_chart.Path') as mock_path:
            # Mock Path to return our temp docs directory
            def path_side_effect(path_str):
                if path_str == "docs":
                    return docs_dir
                return Path(path_str)
            mock_path.side_effect = path_side_effect
            
            generate_chart.export_chart_data_json(df)
            
            # Verify JSON file was created and contains expected data
            self.assertTrue(json_file.exists())
            
            with open(json_file, 'r') as f:
                chart_data = json.load(f)
            
            # Verify structure
            self.assertIn('labels', chart_data)
            self.assertIn('datasets', chart_data)
            self.assertEqual(len(chart_data['labels']), 2)
            self.assertTrue(len(chart_data['datasets']) > 0)
            
            # Verify we have datasets for each agent (total, merged, percentage)
            dataset_labels = [ds['label'] for ds in chart_data['datasets']]
            expected_agents = ['Copilot', 'Codex', 'Cursor', 'Devin']
            for agent in expected_agents:
                self.assertTrue(any(agent in label for label in dataset_labels))

    def test_data_validation_edge_cases(self):
        """Test handling of edge cases in data processing."""
        # Test with empty CSV
        empty_csv = self.temp_path / "empty.csv"
        empty_csv.write_text("timestamp,copilot_total,copilot_merged,codex_total,codex_merged,cursor_total,cursor_merged,devin_total,devin_merged\n")
        
        result = generate_chart.generate_chart(empty_csv)
        self.assertFalse(result)  # Should return False for empty data
        
        # Test with missing CSV file
        missing_csv = self.temp_path / "missing.csv"
        result = generate_chart.generate_chart(missing_csv)
        self.assertFalse(result)  # Should return False for missing file

    def test_percentage_calculations(self):
        """Test that percentage calculations handle edge cases correctly."""
        # Create DataFrame with edge cases (zero totals)
        df = pd.DataFrame({
            'timestamp': ['2025-06-01 10:00:00'],
            'copilot_total': [1000],
            'copilot_merged': [400],
            'codex_total': [0],  # Zero total
            'codex_merged': [0],
            'cursor_total': [100],
            'cursor_merged': [0],  # Zero merged
            'devin_total': [0],   # Zero total
            'devin_merged': [0]
        })
        
        # Test that percentage calculation doesn't crash with zero division
        with patch('generate_chart.Path') as mock_path:
            mock_readme = self.temp_path / "test_readme.md"
            mock_readme.write_text("# Test\n\n## Current Statistics\n\nOld content")
            mock_path.return_value = mock_readme
            
            result = generate_chart.update_readme(df)
            self.assertTrue(result)
            
            # Verify zero division is handled
            content = mock_readme.read_text()
            self.assertIn("0.00%", content)  # Should show 0.00% for zero cases


def run_tests():
    """Run all tests and return results."""
    # Run tests and capture results
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPRTracker)
    runner = unittest.TextTestRunner(verbosity=2, stream=open('/dev/null', 'w'))
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall: {'PASS' if success else 'FAIL'}")
    return success


if __name__ == '__main__':
    run_tests()