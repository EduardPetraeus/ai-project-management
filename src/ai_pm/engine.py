"""Task engine with state machine, dependency resolution, and critical path."""

from __future__ import annotations

from collections import defaultdict, deque
from enum import Enum


class TaskStatus(Enum):
    BACKLOG = "backlog"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


# Valid state transitions
VALID_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.BACKLOG: {TaskStatus.READY, TaskStatus.BLOCKED},
    TaskStatus.READY: {TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED},
    TaskStatus.IN_PROGRESS: {TaskStatus.REVIEW, TaskStatus.BLOCKED},
    TaskStatus.REVIEW: {TaskStatus.DONE, TaskStatus.IN_PROGRESS},
    TaskStatus.BLOCKED: {TaskStatus.BACKLOG, TaskStatus.READY},
    TaskStatus.DONE: set(),  # Terminal state
}


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, task_id: str, current: TaskStatus, target: TaskStatus):
        self.task_id = task_id
        self.current = current
        self.target = target
        super().__init__(f"Task {task_id}: cannot transition from {current.value} to {target.value}")


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected."""

    def __init__(self, cycles: list[list[str]]):
        self.cycles = cycles
        cycle_strs = [" -> ".join(c) for c in cycles]
        super().__init__(f"Circular dependencies detected: {'; '.join(cycle_strs)}")


class TaskEngine:
    """Engine for managing task lifecycle and dependencies."""

    def __init__(self, tasks: list[dict] | None = None):
        self.tasks: dict[str, dict] = {t["id"]: t for t in (tasks or [])}

    def add_task(self, task: dict) -> None:
        """Add a task to the engine."""
        self.tasks[task["id"]] = task

    def get_task(self, task_id: str) -> dict | None:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def transition(self, task_id: str, new_status: TaskStatus) -> bool:
        """Attempt a state transition.

        Args:
            task_id: The task ID to transition.
            new_status: The target status.

        Returns:
            True if the transition was valid and applied.

        Raises:
            KeyError: If the task does not exist.
            InvalidTransitionError: If the transition is not valid.
        """
        task = self.tasks[task_id]
        current_status = TaskStatus(task["status"])

        if new_status not in VALID_TRANSITIONS[current_status]:
            raise InvalidTransitionError(task_id, current_status, new_status)

        task["status"] = new_status.value
        return True

    def resolve_dependencies(self) -> list[str]:
        """Topological sort of tasks by dependencies.

        Returns:
            List of task IDs in dependency order (tasks with no deps first).

        Raises:
            CircularDependencyError: If circular dependencies exist.
        """
        cycles = self.detect_circular_dependencies()
        if cycles:
            raise CircularDependencyError(cycles)

        # Build in-degree map and adjacency list
        in_degree: dict[str, int] = {tid: 0 for tid in self.tasks}
        dependents: dict[str, list[str]] = defaultdict(list)

        for tid, task in self.tasks.items():
            deps = task.get("depends_on", []) or []
            for dep in deps:
                if dep in self.tasks:
                    in_degree[tid] += 1
                    dependents[dep].append(tid)

        # Kahn's algorithm
        queue = deque(sorted(tid for tid, deg in in_degree.items() if deg == 0))
        result: list[str] = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for dependent in sorted(dependents[current]):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self.tasks):
            # Should not happen since we checked for cycles above
            raise CircularDependencyError([["unresolved"]])

        return result

    def detect_circular_dependencies(self) -> list[list[str]]:
        """Find all circular dependency chains.

        Returns:
            List of cycles, where each cycle is a list of task IDs.
        """
        # Build adjacency list (task -> tasks it depends on)
        graph: dict[str, list[str]] = {}
        for tid, task in self.tasks.items():
            deps = task.get("depends_on", []) or []
            graph[tid] = [d for d in deps if d in self.tasks]

        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def _dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    _dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle — extract it
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.discard(node)

        for node in sorted(self.tasks.keys()):
            if node not in visited:
                _dfs(node)

        return cycles

    def critical_path(self) -> list[str]:
        """Calculate the critical path (longest dependency chain to completion).

        The critical path is the longest chain of dependent tasks.
        Only considers tasks that are not yet done.

        Returns:
            List of task IDs forming the critical path.
        """
        # Filter to non-done tasks
        active_tasks = {tid: task for tid, task in self.tasks.items() if task.get("status") != "done"}

        if not active_tasks:
            return []

        # Build adjacency: task -> tasks that depend on it
        dependents: dict[str, list[str]] = defaultdict(list)
        for tid, task in active_tasks.items():
            for dep in task.get("depends_on", []) or []:
                if dep in active_tasks:
                    dependents[dep].append(tid)

        # Calculate longest path from each node using memoization
        longest_from: dict[str, list[str]] = {}

        def _longest(node: str) -> list[str]:
            if node in longest_from:
                return longest_from[node]

            if node not in active_tasks:
                longest_from[node] = []
                return []

            best: list[str] = []
            for dep in dependents.get(node, []):
                candidate = _longest(dep)
                if len(candidate) > len(best):
                    best = candidate

            result = [node] + best
            longest_from[node] = result
            return result

        # Find roots (tasks with no unfinished dependencies)
        roots = []
        for tid, task in active_tasks.items():
            deps = task.get("depends_on", []) or []
            active_deps = [d for d in deps if d in active_tasks]
            if not active_deps:
                roots.append(tid)

        # Compute longest path from each root
        overall_best: list[str] = []
        for root in sorted(roots):
            path = _longest(root)
            if len(path) > len(overall_best):
                overall_best = path

        return overall_best

    def filter_tasks(
        self,
        status: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        tags: list[str] | None = None,
    ) -> list[dict]:
        """Filter tasks by various criteria.

        Args:
            status: Filter by task status.
            priority: Filter by priority level.
            assignee: Filter by assignee.
            tags: Filter by tags (any match).

        Returns:
            List of matching task dictionaries.
        """
        results = list(self.tasks.values())

        if status is not None:
            results = [t for t in results if t.get("status") == status]

        if priority is not None:
            results = [t for t in results if t.get("priority") == priority]

        if assignee is not None:
            results = [t for t in results if t.get("assignee") == assignee]

        if tags is not None:
            tag_set = set(tags)
            results = [t for t in results if tag_set & set(t.get("tags", []))]

        return results

    def pick_next(self, agent_type: str | None = None) -> dict | None:
        """Pick the highest-priority ready task.

        Args:
            agent_type: Optional agent type filter.

        Returns:
            The best available task, or None.
        """
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        candidates = self.filter_tasks(status="ready")

        if agent_type:
            candidates = [t for t in candidates if t.get("agent") == agent_type]

        # Only tasks with resolved dependencies
        ready = []
        for task in candidates:
            deps = task.get("depends_on", []) or []
            all_done = all(self.tasks.get(d, {}).get("status") == "done" for d in deps)
            if all_done and task.get("assignee") is None:
                ready.append(task)

        if not ready:
            return None

        # Sort by priority, then by task ID
        ready.sort(key=lambda t: (priority_order.get(t.get("priority", "medium"), 2), t.get("id", "")))
        return ready[0]
