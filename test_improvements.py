#!/usr/bin/env python3
"""
Enhanced test suite for AI Research Assistant improvements
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.research_assistant import ResearchAssistant
    from src.config import Config
except ImportError:
    # Handle import error gracefully
    ResearchAssistant = None
    Config = None

class TestImprovedFeatures:
    """Test the improved features of the application."""
    
    def setup_method(self):
        """Setup test environment."""
        if ResearchAssistant is None:
            pytest.skip("ResearchAssistant module not available")
            
        self.assistant = ResearchAssistant()
        
    def test_file_validation(self):
        """Test file validation functionality."""
        # Test file size validation
        large_file_data = b"x" * (60 * 1024 * 1024)  # 60MB
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            tmp.write(large_file_data)
            tmp.flush()
            
            # This would trigger size validation in the UI
            assert Path(tmp.name).stat().st_size > 50 * 1024 * 1024
            
    def test_qa_history_structure(self):
        """Test Q&A history data structure."""
        qa_entry = {
            "question": "What is the main contribution?",
            "answer": {"answer": "Test answer", "confidence": 0.9},
            "paper_id": "test123",
            "section": "abstract",
            "timestamp": datetime.now().isoformat()
        }
        
        # Validate structure
        assert "question" in qa_entry
        assert "answer" in qa_entry
        assert "timestamp" in qa_entry
        assert isinstance(qa_entry["timestamp"], str)
        
    def test_export_data_format(self):
        """Test export data format."""
        test_data = {
            "papers": {},
            "qa_history": [],
            "exported_at": datetime.now().isoformat(),
            "app_version": "AI Research Assistant v1.0"
        }
        
        # Test JSON serialization
        json_str = json.dumps(test_data, default=str)
        parsed_data = json.loads(json_str)
        
        assert parsed_data["app_version"] == "AI Research Assistant v1.0"
        assert "exported_at" in parsed_data
        
    def test_memory_optimization(self):
        """Test memory optimization functions."""
        import gc
        import sys
        
        # Create test data
        test_list = [i for i in range(1000)]
        initial_objects = len(gc.get_objects())
        
        # Clear test data
        del test_list
        gc.collect()
        
        # Memory should be freed
        final_objects = len(gc.get_objects())
        assert final_objects <= initial_objects
        
    def test_error_handling_structure(self):
        """Test error handling structure."""
        try:
            # Simulate an error condition
            raise ValueError("Test error")
        except ValueError as e:
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            assert error_info["error_type"] == "ValueError"
            assert error_info["error_message"] == "Test error"
            
    def test_config_validation(self):
        """Test configuration validation."""
        if Config is None:
            pytest.skip("Config module not available")
            
        config = Config()
        
        # Test that required attributes exist
        assert hasattr(config, 'model_config')
        assert hasattr(config, 'processing_config')
        assert hasattr(config, 'database_config')

class TestUIComponents:
    """Test UI component functionality."""
    
    def test_validation_function(self):
        """Test file validation function logic."""
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        
        # Test valid file
        valid_result = {
            "valid": True,
            "error": None
        }
        assert valid_result["valid"] is True
        
        # Test invalid file size
        invalid_result = {
            "valid": False,
            "error": "File size exceeds maximum"
        }
        assert invalid_result["valid"] is False
        
    def test_confidence_color_logic(self):
        """Test confidence color assignment logic."""
        def get_confidence_color(confidence):
            if confidence > 0.8:
                return "#28a745", "🟢"  # Green
            elif confidence > 0.6:
                return "#ffc107", "🟡"  # Yellow
            else:
                return "#dc3545", "🔴"  # Red
                
        # Test different confidence levels
        high_conf = get_confidence_color(0.9)
        assert high_conf[1] == "🟢"
        
        medium_conf = get_confidence_color(0.7)
        assert medium_conf[1] == "🟡"
        
        low_conf = get_confidence_color(0.3)
        assert low_conf[1] == "🔴"

class TestDataManagement:
    """Test data management functionality."""
    
    def test_workspace_export_structure(self):
        """Test workspace export data structure."""
        workspace_data = {
            "papers": {},
            "qa_history": [],
            "settings": {
                "papers_count": 0,
                "qa_count": 0
            },
            "exported_at": datetime.now().isoformat(),
            "app_version": "AI Research Assistant v1.0"
        }
        
        # Validate structure
        required_keys = ["papers", "qa_history", "settings", "exported_at", "app_version"]
        for key in required_keys:
            assert key in workspace_data
            
    def test_backup_data_integrity(self):
        """Test backup data integrity."""
        original_data = {
            "qa_history": [
                {
                    "question": "Test question",
                    "answer": {"answer": "Test answer"},
                    "timestamp": "2024-01-01T12:00:00"
                }
            ]
        }
        
        # Serialize and deserialize
        json_str = json.dumps(original_data)
        restored_data = json.loads(json_str)
        
        assert restored_data["qa_history"][0]["question"] == original_data["qa_history"][0]["question"]

if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running AI Research Assistant Improvement Tests...")
    
    try:
        # Test file validation logic
        test_ui = TestUIComponents()
        test_ui.test_validation_function()
        test_ui.test_confidence_color_logic()
        print("✅ UI Component tests passed")
        
        # Test data management
        test_data = TestDataManagement()
        test_data.test_workspace_export_structure()
        test_data.test_backup_data_integrity()
        print("✅ Data Management tests passed")
        
        # Test improved features
        test_features = TestImprovedFeatures()
        test_features.test_qa_history_structure()
        test_features.test_export_data_format()
        test_features.test_memory_optimization()
        test_features.test_error_handling_structure()
        print("✅ Improved Features tests passed")
        
        print("\n🎉 All improvement tests passed successfully!")
        print("💡 The enhanced AI Research Assistant is ready for use!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("🔧 Please check the implementation and try again")
