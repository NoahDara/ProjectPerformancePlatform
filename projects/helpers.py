from django.utils import timezone

from benchmarking.models import ProjectSnapshot


def create_project_snapshot(project):
    """
    Creates or updates a ProjectSnapshot when a project is marked as completed.
    Calculates SPI, CPI, team size, discipline mix, and final costs.
    """
    disciplines = project.disciplines.filter(is_active=True)

    # --- Discipline Mix ---
    discipline_codes = sorted([
        pd.discipline.code for pd in disciplines if hasattr(pd.discipline, 'code')
    ])
    discipline_mix = ",".join(discipline_codes)

    # --- Actual Duration ---
    start = project.baseline_start_date or project.start_date
    end = project.actual_end_date or timezone.now().date()
    actual_duration = (end - start).days

    # --- SPI (Schedule Performance Index) ---
    # SPI = % complete / % of planned time elapsed
    baseline_duration = (
        (project.baseline_end_date - project.baseline_start_date).days
        if project.baseline_start_date and project.baseline_end_date
        else actual_duration
    )
    planned_duration_ratio = actual_duration / baseline_duration if baseline_duration else 1
    overall_percent_complete = sum(
        (pd.planned_weight / 100) * pd.percent_complete for pd in disciplines
    )
    final_spi = round(
        overall_percent_complete / planned_duration_ratio if planned_duration_ratio else 0, 4
    )

    # --- Final Cost & CPI ---
    final_cost = sum(
        expense.amount
        for expense in project.expenses.filter(status="Confirmed")
    )
    budget_at_completion = project.baseline_budget or project.budget
    final_cpi = round(
        budget_at_completion / final_cost if final_cost else 0, 4
    )

    # --- Team Size ---
    # Unique employees: discipline managers + task assignees
    employee_ids = set()
    for pd in disciplines:
        if pd.manager_id:
            employee_ids.add(pd.manager_id)
        for task in pd.tasks.filter(is_active=True):
            if task.assigned_to_id:
                employee_ids.add(task.assigned_to_id)
    team_size = len(employee_ids)

    # --- Create or Update Snapshot ---
    snapshot, created = ProjectSnapshot.objects.update_or_create(
        project=project,
        defaults={
            "discipline_mix": discipline_mix,
            "actual_duration": max(actual_duration, 0),
            "final_spi": final_spi,
            "final_cpi": final_cpi,
            "team_size": team_size,
            "final_cost": final_cost,
            "budget_at_completion": budget_at_completion,
        }
    )
    return snapshot