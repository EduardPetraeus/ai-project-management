"""Tests for the task engine — state machine, dependencies, critical path, filtering."""

import pytest

from ai_pm.engine import (
    VALID_TRANSITIONS,
    CircularDependencyError,
    InvalidTransitionError,
    TaskEngine,
    TaskStatus,
)


class TestStateTransitions:
    """Test the state machine transitions."""

    def test_valid_transitions_from_backlog(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        # backlog -> ready is valid
        task = {"id": "TASK-010", "title": "Test", "status": "backlog", "priority": "low"}
        engine.add_task(task)
        assert engine.transition("TASK-010", TaskStatus.READY) is True
        assert engine.tasks["TASK-010"]["status"] == "ready"

    def test_valid_transition_ready_to_in_progress(self):
        engine = TaskEngine([{"id": "TASK-001", "title": "T", "status": "ready", "priority": "high"}])
        assert engine.transition("TASK-001", TaskStatus.IN_PROGRESS) is True
        assert engine.tasks["TASK-001"]["status"] == "in_progress"

    def test_valid_transition_in_progress_to_review(self):
        engine = TaskEngine([{"id": "TASK-001", "title": "T", "status": "in_progress", "priority": "high"}])
        assert engine.transition("TASK-001", TaskStatus.REVIEW) is True
        assert engine.tasks["TASK-001"]["status"] == "review"

    def test_valid_transition_review_to_done(self):
        engine = TaskEngine([{"id": "TASK-001", "title": "T", "status": "review", "priority": "high"}])
        assert engine.transition("TASK-001", TaskStatus.DONE) is True
        assert engine.tasks["TASK-001"]["status"] == "done"

    def test_valid_transition_to_blocked(self):
        engine = TaskEngine([{"id": "TASK-001", "title": "T", "status": "ready", "priority": "high"}])
        assert engine.transition("TASK-001", TaskStatus.BLOCKED) is True
        assert engine.tasks["TASK-001"]["status"] == "blocked"

    def test_valid_transition_blocked_to_ready(self):
        engine = TaskEngine([{"id": "TASK-001", "title": "T", "status": "blocked", "priority": "high"}])
        assert engine.transition("TASK-001", TaskStatus.READY) is True
        assert engine.tasks["TASK-001"]["status"] == "ready"

    def test_invalid_transition_done_to_anything(self):
        engine = TaskEngine([{"id": "TASK-001", "title": "T", "status": "done", "priority": "high"}])
        with pytest.raises(InvalidTransitionError):
            engine.transition("TASK-001", TaskStatus.BACKLOG)

    def test_invalid_transition_backlog_to_done(self):
        engine = TaskEngine([{"id": "TASK-001", "title": "T", "status": "backlog", "priority": "high"}])
        with pytest.raises(InvalidTransitionError):
            engine.transition("TASK-001", TaskStatus.DONE)

    def test_invalid_transition_backlog_to_in_progress(self):
        engine = TaskEngine([{"id": "TASK-001", "title": "T", "status": "backlog", "priority": "high"}])
        with pytest.raises(InvalidTransitionError):
            engine.transition("TASK-001", TaskStatus.IN_PROGRESS)

    def test_transition_nonexistent_task(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        with pytest.raises(KeyError):
            engine.transition("TASK-999", TaskStatus.DONE)

    def test_review_to_in_progress_rework(self):
        """Review can be sent back to in_progress for rework."""
        engine = TaskEngine([{"id": "TASK-001", "title": "T", "status": "review", "priority": "high"}])
        assert engine.transition("TASK-001", TaskStatus.IN_PROGRESS) is True
        assert engine.tasks["TASK-001"]["status"] == "in_progress"

    def test_done_is_terminal(self):
        """Done state has no valid outgoing transitions."""
        assert VALID_TRANSITIONS[TaskStatus.DONE] == set()


class TestDependencyResolution:
    """Test topological sort and dependency resolution."""

    def test_simple_chain(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        order = engine.resolve_dependencies()
        # TASK-001 must come before TASK-002, TASK-002 before TASK-003
        assert order.index("TASK-001") < order.index("TASK-002")
        assert order.index("TASK-002") < order.index("TASK-003")

    def test_no_dependencies(self):
        tasks = [
            {"id": "TASK-001", "title": "A", "status": "ready", "priority": "low", "depends_on": []},
            {"id": "TASK-002", "title": "B", "status": "ready", "priority": "low", "depends_on": []},
        ]
        engine = TaskEngine(tasks)
        order = engine.resolve_dependencies()
        assert len(order) == 2
        assert set(order) == {"TASK-001", "TASK-002"}

    def test_circular_raises(self, circular_tasks):
        engine = TaskEngine(circular_tasks)
        with pytest.raises(CircularDependencyError):
            engine.resolve_dependencies()

    def test_complex_dag(self):
        """Diamond dependency pattern: A -> B,C -> D."""
        tasks = [
            {"id": "TASK-001", "title": "A", "status": "ready", "priority": "high", "depends_on": []},
            {"id": "TASK-002", "title": "B", "status": "ready", "priority": "high", "depends_on": ["TASK-001"]},
            {"id": "TASK-003", "title": "C", "status": "ready", "priority": "high", "depends_on": ["TASK-001"]},
            {
                "id": "TASK-004",
                "title": "D",
                "status": "ready",
                "priority": "high",
                "depends_on": ["TASK-002", "TASK-003"],
            },
        ]
        engine = TaskEngine(tasks)
        order = engine.resolve_dependencies()
        assert order[0] == "TASK-001"
        assert order[-1] == "TASK-004"
        assert order.index("TASK-002") < order.index("TASK-004")
        assert order.index("TASK-003") < order.index("TASK-004")

    def test_resolve_with_external_deps(self):
        """Dependencies on non-existent tasks are ignored."""
        tasks = [
            {"id": "TASK-001", "title": "A", "status": "ready", "priority": "high", "depends_on": ["TASK-999"]},
        ]
        engine = TaskEngine(tasks)
        order = engine.resolve_dependencies()
        assert order == ["TASK-001"]


class TestCircularDependencyDetection:
    """Test circular dependency detection."""

    def test_no_cycles(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        cycles = engine.detect_circular_dependencies()
        assert cycles == []

    def test_direct_cycle(self, circular_tasks):
        engine = TaskEngine(circular_tasks)
        cycles = engine.detect_circular_dependencies()
        assert len(cycles) > 0

    def test_self_referencing(self):
        tasks = [
            {"id": "TASK-001", "title": "A", "status": "backlog", "priority": "high", "depends_on": ["TASK-001"]},
        ]
        engine = TaskEngine(tasks)
        cycles = engine.detect_circular_dependencies()
        assert len(cycles) > 0

    def test_no_tasks(self):
        engine = TaskEngine([])
        cycles = engine.detect_circular_dependencies()
        assert cycles == []


class TestCriticalPath:
    """Test critical path calculation."""

    def test_simple_chain(self):
        tasks = [
            {"id": "TASK-001", "title": "A", "status": "ready", "priority": "high", "depends_on": []},
            {"id": "TASK-002", "title": "B", "status": "blocked", "priority": "high", "depends_on": ["TASK-001"]},
            {"id": "TASK-003", "title": "C", "status": "blocked", "priority": "high", "depends_on": ["TASK-002"]},
        ]
        engine = TaskEngine(tasks)
        path = engine.critical_path()
        assert path == ["TASK-001", "TASK-002", "TASK-003"]

    def test_parallel_paths_picks_longest(self):
        tasks = [
            {"id": "TASK-001", "title": "A", "status": "ready", "priority": "high", "depends_on": []},
            {"id": "TASK-002", "title": "B", "status": "blocked", "priority": "high", "depends_on": ["TASK-001"]},
            {"id": "TASK-003", "title": "C", "status": "blocked", "priority": "high", "depends_on": ["TASK-002"]},
            {"id": "TASK-004", "title": "D", "status": "ready", "priority": "high", "depends_on": []},
        ]
        engine = TaskEngine(tasks)
        path = engine.critical_path()
        # The longest chain is TASK-001 -> TASK-002 -> TASK-003 (length 3)
        assert len(path) == 3
        assert path == ["TASK-001", "TASK-002", "TASK-003"]

    def test_all_done_returns_empty(self):
        tasks = [
            {"id": "TASK-001", "title": "A", "status": "done", "priority": "high", "depends_on": []},
        ]
        engine = TaskEngine(tasks)
        assert engine.critical_path() == []

    def test_no_tasks(self):
        engine = TaskEngine([])
        assert engine.critical_path() == []

    def test_single_task(self):
        tasks = [{"id": "TASK-001", "title": "A", "status": "ready", "priority": "high", "depends_on": []}]
        engine = TaskEngine(tasks)
        assert engine.critical_path() == ["TASK-001"]


class TestFiltering:
    """Test task filtering."""

    def test_filter_by_status(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        ready = engine.filter_tasks(status="ready")
        assert len(ready) == 1
        assert ready[0]["id"] == "TASK-002"

    def test_filter_by_priority(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        high = engine.filter_tasks(priority="high")
        assert len(high) == 2

    def test_filter_by_assignee(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        assigned = engine.filter_tasks(assignee="session-001")
        assert len(assigned) == 1
        assert assigned[0]["id"] == "TASK-001"

    def test_filter_by_tags(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        backend = engine.filter_tasks(tags=["backend"])
        assert len(backend) == 2

    def test_filter_no_match(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        result = engine.filter_tasks(status="nonexistent")
        assert result == []

    def test_filter_combined(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        result = engine.filter_tasks(status="done", priority="high")
        assert len(result) == 1
        assert result[0]["id"] == "TASK-001"

    def test_filter_tags_any_match(self):
        tasks = [
            {"id": "TASK-001", "title": "A", "status": "ready", "tags": ["a", "b"]},
            {"id": "TASK-002", "title": "B", "status": "ready", "tags": ["c"]},
        ]
        engine = TaskEngine(tasks)
        result = engine.filter_tasks(tags=["b", "c"])
        assert len(result) == 2


class TestPickNext:
    """Test pick_next task selection."""

    def test_picks_highest_priority_ready(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        picked = engine.pick_next()
        assert picked is not None
        assert picked["id"] == "TASK-002"

    def test_picks_by_agent_type(self, sample_tasks):
        engine = TaskEngine(sample_tasks)
        picked = engine.pick_next(agent_type="test")
        # TASK-003 is test but blocked, so no match
        assert picked is None

    def test_no_ready_tasks(self):
        tasks = [{"id": "TASK-001", "title": "A", "status": "done", "priority": "high", "depends_on": []}]
        engine = TaskEngine(tasks)
        assert engine.pick_next() is None

    def test_respects_unresolved_deps(self):
        tasks = [
            {"id": "TASK-001", "title": "A", "status": "in_progress", "priority": "high", "depends_on": []},
            {
                "id": "TASK-002",
                "title": "B",
                "status": "ready",
                "priority": "high",
                "depends_on": ["TASK-001"],
                "assignee": None,
            },
        ]
        engine = TaskEngine(tasks)
        # TASK-002 is ready but depends on TASK-001 which is not done
        assert engine.pick_next() is None
