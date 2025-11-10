"""Integration tests for end-to-end workflows."""

import pytest
from pathlib import Path
from core.excel_loader import process_excel
from core.models import build_course_groups
from algorithms import get_registered_scheduler


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_workflow_dfs(self):
        """Test complete workflow: load Excel → run DFS → generate schedules."""
        # Load courses
        excel_path = Path(__file__).parent.parent / "data" / "sample_isik_courses.xlsx"
        if not excel_path.exists():
            pytest.skip("Sample data file not found")
        
        courses = process_excel(str(excel_path))
        assert len(courses) > 0
        
        # Build course groups
        course_groups = build_course_groups(courses)
        
        # Get scheduler
        scheduler_cls = get_registered_scheduler("DFS")
        assert scheduler_cls is not None
        
        # Create scheduler (SchedulerPrefs kullanmadan)
        scheduler = scheduler_cls(
            max_results=5,
            max_ects=42,
            allow_conflicts=True,
            max_conflicts=1,
            timeout_seconds=30
        )
        
        # Select a few courses
        selected_courses = courses[:10]
        
        # Generate schedules
        schedules = scheduler.generate_schedules(
            course_groups=course_groups,
            mandatory_codes={c.main_code for c in selected_courses[:5]},
            optional_codes={c.main_code for c in selected_courses[5:]}
        )
        
        # Verify results
        assert len(schedules) > 0
        assert all(s.total_credits <= 42 for s in schedules)
    
    def test_multiple_algorithms(self):
        """Test running multiple algorithms on same data."""
        excel_path = Path(__file__).parent.parent / "data" / "sample_isik_courses.xlsx"
        if not excel_path.exists():
            pytest.skip("Sample data file not found")
        
        courses = process_excel(str(excel_path))
        selected_courses = courses[:8]
        
        # Build course groups
        course_groups = build_course_groups(courses)
        
        algorithms = ["DFS", "BFS", "Greedy"]
        results = {}
        
        for algo_name in algorithms:
            scheduler_cls = get_registered_scheduler(algo_name)
            if scheduler_cls is None:
                continue
                
            scheduler = scheduler_cls(
                max_results=3,
                max_ects=30,
                timeout_seconds=10
            )
            
            schedules = scheduler.generate_schedules(
                course_groups=course_groups,
                mandatory_codes={c.main_code for c in selected_courses}
            )
            
            results[algo_name] = schedules
        
        # All algorithms should find at least one schedule
        assert all(len(schedules) > 0 for schedules in results.values())
    
    def test_export_workflow(self):
        """Test export workflow after generating schedules."""
        import tempfile
        from reporting import save_schedules_as_pdf, export_to_excel
        
        excel_path = Path(__file__).parent.parent / "data" / "sample_isik_courses.xlsx"
        if not excel_path.exists():
            pytest.skip("Sample data file not found")
        
        # Generate schedules
        courses = process_excel(str(excel_path))
        course_groups = build_course_groups(courses)
        
        scheduler_cls = get_registered_scheduler("DFS")
        if scheduler_cls is None:
            pytest.skip("DFS scheduler not found")
            
        scheduler = scheduler_cls(max_results=2, max_ects=30, timeout_seconds=10)
        
        selected_courses = courses[:6]
        schedules = scheduler.generate_schedules(
            course_groups=course_groups,
            mandatory_codes={c.main_code for c in selected_courses}
        )
        
        assert len(schedules) > 0
        
        # Test PDF export
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "export_test.pdf"
            save_schedules_as_pdf(schedules, str(pdf_path))
            assert pdf_path.exists()
            
            # Test Excel export
            excel_export_path = Path(tmpdir) / "export_test.xlsx"
            export_to_excel(schedules, str(excel_export_path))
            assert excel_export_path.exists()


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def test_invalid_excel_file(self):
        """Test handling of invalid Excel file."""
        with pytest.raises(Exception):
            process_excel("nonexistent_file.xlsx")
    
    def test_empty_course_list(self):
        """Test scheduler with empty course list."""
        scheduler_cls = get_registered_scheduler("DFS")
        if scheduler_cls is None:
            pytest.skip("DFS scheduler not found")
            
        scheduler = scheduler_cls(max_results=1)
        
        schedules = scheduler.generate_schedules(
            course_groups={},
            mandatory_codes=set()
        )
        
        # Should return empty list, not crash
        assert schedules == []
    
    def test_impossible_constraints(self):
        """Test scheduler with impossible constraints."""
        excel_path = Path(__file__).parent.parent / "data" / "sample_isik_courses.xlsx"
        if not excel_path.exists():
            pytest.skip("Sample data file not found")
        
        courses = process_excel(str(excel_path))
        course_groups = build_course_groups(courses)
        
        scheduler_cls = get_registered_scheduler("DFS")
        if scheduler_cls is None:
            pytest.skip("DFS scheduler not found")
            
        scheduler = scheduler_cls(
            max_results=5,
            max_ects=6,  # Too low to fit any meaningful schedule
            timeout_seconds=5
        )
        
        schedules = scheduler.generate_schedules(
            course_groups=course_groups,
            mandatory_codes={c.main_code for c in courses[:10]}
        )
        
        # Should handle gracefully, possibly returning empty list
        assert isinstance(schedules, list)
