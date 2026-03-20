from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Avg, Count, Q

from benchmarking.models import ProjectSnapshot
from projects.models import Project, ProjectDiscipline
from tasks.models import TaskUpdate
from expenses.models import Expense


class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()
        in_60  = today + timedelta(days=60)

        # ── Active projects ──────────────────────────────────────
        active_qs = Project.objects.filter(
            is_active=True, is_deleted=False,
            status__in=["planning", "in_progress", "on_hold"]
        ).select_related("client", "branch", "project_manager")

        # Attach a percent_complete to each project
        # (weighted avg of discipline percent_complete values)
        active_projects = []
        for p in active_qs:
            disciplines = p.disciplines.filter(is_active=True)
            if disciplines.exists():
                total_weight = sum(d.planned_weight for d in disciplines)
                weighted = sum(
                    d.percent_complete * d.planned_weight for d in disciplines
                )
                p.percent_complete = round(
                    weighted / total_weight, 1
                ) if total_weight else 0
            else:
                p.percent_complete = 0
            active_projects.append(p)

        ctx["active_projects"]       = active_projects
        ctx["active_projects_count"] = len(active_projects)

        # ── All projects (for total count + donut) ───────────────
        all_projects = Project.objects.filter(is_active=True, is_deleted=False)
        total = all_projects.count()
        ctx["total_projects_count"] = total

        STATUS_COLORS = {
            "in_progress": "var(--teal)",
            "planning":    "var(--blue)",
            "on_hold":     "var(--amber)",
            "completed":   "var(--green)",
        }
        CIRCUMFERENCE = 289  # 2π × r where r=46

        breakdown = []
        offset = 0
        for status, color in STATUS_COLORS.items():
            count = all_projects.filter(status=status).count()
            pct   = round((count / total) * 100) if total else 0
            dash  = round((count / total) * CIRCUMFERENCE) if total else 0
            breakdown.append({
                "label":  dict(Project.STATUS_CHOICES).get(status, status),
                "count":  count,
                "pct":    pct,
                "color":  color,
                "dash":   dash,
                "offset": offset,
            })
            offset += dash

        ctx["status_breakdown"]  = breakdown
        ctx["in_progress_pct"]   = breakdown[0]["dash"]
        ctx["planning_pct"]      = breakdown[1]["dash"]
        ctx["on_hold_pct"]       = breakdown[2]["dash"]
        ctx["planning_offset"]   = breakdown[0]["dash"] + breakdown[2]["dash"]

        # ── Portfolio budget ─────────────────────────────────────
        total_budget = sum(
            p.budget for p in all_projects.prefetch_related("disciplines")
        )
        ctx["total_budget_m"] = round(total_budget / 1_000_000, 1)

        # ── Avg SPI / CPI from snapshots ─────────────────────────
        snapshots = ProjectSnapshot.objects.filter(
            project__in=all_projects, is_active=True
        )
        agg = snapshots.aggregate(
            avg_spi=Avg("final_spi"),
            avg_cpi=Avg("final_cpi"),
        )
        ctx["avg_spi"] = round(agg["avg_spi"] or 0, 2)
        ctx["avg_cpi"] = round(agg["avg_cpi"] or 0, 2)

        # ── Performance index rings ──────────────────────────────
        RING_MAX = 201  # 2π × r where r=32
        spi = ctx["avg_spi"]
        cpi = ctx["avg_cpi"]

        def ring(value, label, title, description):
            clamped  = min(value / 1.2, 1.0)          # 1.2 = "full ring"
            dash     = round(clamped * RING_MAX)
            good     = value >= 1.0
            color    = "var(--green)" if good else (
                       "var(--amber)" if value >= 0.9 else "var(--red)")
            trend_c  = "up" if good else "down"
            return {
                "value": value, "label": label,
                "title": title, "description": description,
                "dash": dash, "color": color,
                "trend_class": trend_c,
                "trend_icon":  "arrow-up" if good else "arrow-down",
                "trend_label": "On target" if good else "Needs attention",
            }

        ctx["performance_indices"] = [
            ring(spi, "SPI", "Schedule Performance",
                 "Ratio of earned value to planned value. < 1 means behind schedule."),
            ring(cpi, "CPI", "Cost Performance",
                 "Ratio of earned value to actual cost. > 1 means under budget."),
        ]

        # ── Budget by discipline ─────────────────────────────────
        discipline_budgets = []
        disc_agg = (
            ProjectDiscipline.objects
            .filter(is_active=True, is_deleted=False)
            .values("discipline__name")
            .annotate(total_budget=Sum("budget_allocated"))
            .order_by("-total_budget")
        )
        # Pair with actual expenses per discipline (via project)
        for row in disc_agg:
            budget_k = round(row["total_budget"] / 1000, 1)
            # Expenses tied to projects that have this discipline
            spent = Expense.objects.filter(
                is_active=True,
                status="Confirmed",
                project__disciplines__discipline__name=row["discipline__name"],
            ).aggregate(total=Sum("amount"))["total"] or 0
            spent_k = round(spent / 1000, 1)
            pct = round((spent / row["total_budget"]) * 100) if row["total_budget"] else 0
            discipline_budgets.append({
                "name":     row["discipline__name"],
                "budget_k": budget_k,
                "spent_k":  spent_k,
                "pct":      min(pct, 100),
            })
        ctx["discipline_budgets"] = discipline_budgets[:6]

        # ── Recent task updates (activity feed) ──────────────────
        recent_updates = (
            TaskUpdate.objects
            .filter(is_active=True, is_deleted=False)
            .select_related(
                "submitted_by",
                "task__discipline__project",
            )
            .order_by("-date", "-created")[:10]
        )
        # Attach avatar initials & colours
        AVATAR_PALETTE = [
            ("var(--blue-lt)",  "var(--blue)"),
            ("var(--teal-lt)",  "var(--teal)"),
            ("var(--green-lt)", "var(--green)"),
            ("var(--amber-lt)", "var(--amber)"),
        ]
        updates_with_meta = []
        for i, u in enumerate(recent_updates):
            bg, fg = AVATAR_PALETTE[i % len(AVATAR_PALETTE)]
            name = u.submitted_by.full_name if u.submitted_by else "—"
            initials = "".join(p[0].upper() for p in name.split()[:2])
            u.avatar_bg    = bg
            u.avatar_color = fg
            u.initials     = initials
            updates_with_meta.append(u)
        ctx["recent_updates"] = updates_with_meta

        # ── Upcoming deadlines (next 60 days) ────────────────────
        upcoming_qs = (
            Project.objects
            .filter(
                is_active=True, is_deleted=False,
                status__in=["planning", "in_progress"],
                planned_end_date__range=[today, in_60],
            )
            .order_by("planned_end_date")
        )
        deadlines = []
        for p in upcoming_qs:
            days = (p.planned_end_date - today).days
            if days <= 14:
                dot, icon = "active", "clock"
            elif p.status == "completed":
                dot, icon = "done", "check"
            else:
                dot, icon = "pending", "calendar"
            deadlines.append({
                "project_name":  p.name,
                "label":         p.get_status_display(),
                "due_date":      p.planned_end_date,
                "days_remaining": days,
                "status":        p.status,
                "dot_class":     dot,
                "icon":          icon,
            })
        ctx["upcoming_deadlines"] = deadlines

        # ── Recent expenses ──────────────────────────────────────
        ctx["recent_expenses"] = (
            Expense.objects
            .filter(is_active=True, is_deleted=False)
            .select_related("category", "project")
            .order_by("-expense_date", "-created")[:8]
        )

        ctx["today"] = today
        return ctx