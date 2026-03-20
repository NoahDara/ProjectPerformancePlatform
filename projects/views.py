from helpers.views import SafeListView, SafeUpdateView, SafeDeleteView, ToggleActiveView
from projects.helpers import create_project_snapshot
from .models import Project, ProjectDiscipline
from .forms import ProjectForm, ProjectDisciplineForm
from django.views.generic import CreateView, DetailView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.forms import modelformset_factory
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.utils import timezone

class ProjectListView(LoginRequiredMixin, SafeListView):
    model = Project
    template_name = "projects/index.html"
    context_object_name = "projects"


class ProjectCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Project
    template_name = "projects/create.html"
    form_class = ProjectForm
    success_message = "Project Created Successfully"

    def get_success_url(self):
        return reverse("project-disciplines", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Project
    context_object_name = "project"
    template_name = "projects/update.html"
    form_class = ProjectForm
    success_url = reverse_lazy("project-index")


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object
        from django.utils import timezone
        from django.db.models import Sum

        # Overall weighted progress
        disciplines = project.disciplines.prefetch_related('tasks__updates').all()
        ctx['overall_progress'] = round(sum(
            pd.percent_complete * float(pd.planned_weight) / 100
            for pd in disciplines
        ), 1)
        ctx['total_actual_cost'] = 100
        ctx['budget_remaining'] = float(project.baseline_budget or 0) - ctx['total_actual_cost']
        ctx['budget_variance_pct'] = (
            ctx['total_actual_cost'] / float(project.baseline_budget) * 100
            if project.baseline_budget else None
        )
        if project.baseline_end_date:
            ctx['schedule_variance'] = (project.planned_end_date - project.baseline_end_date).days
        else:
            ctx['schedule_variance'] = 0
        ctx['days_remaining'] = (project.planned_end_date - timezone.now().date()).days
        expenses = project.expenses.all()
        ctx['expense_total'] = expenses.aggregate(t=Sum('amount'))['t'] or 0
        ctx['expense_confirmed'] = expenses.filter(status='Confirmed').aggregate(t=Sum('amount'))['t'] or 0
        ctx['expense_pending'] = expenses.filter(status='Submitted').aggregate(t=Sum('amount'))['t'] or 0

        return ctx

class ProjectDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Project
    success_url = reverse_lazy("project-index")


class ProjectToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Project
    success_url = reverse_lazy("project-index")


class ProjectDisciplineUpdateView(LoginRequiredMixin, View):
    template_name = "projects/disciplines/update.html"

    def get_project(self, pk):
        return get_object_or_404(Project, pk=pk)

    def get_formset_class(self):
        return modelformset_factory(
            ProjectDiscipline,
            form=ProjectDisciplineForm,
            extra=0,
        )

    def get(self, request, pk):
        project = self.get_project(pk)
        ProjectDisciplineFormSet = self.get_formset_class()
        formset = ProjectDisciplineFormSet(
            queryset=ProjectDiscipline.objects.filter(project=project).select_related('discipline', 'manager')
        )
        return render(request, self.template_name, {
            "project": project,
            "formset": formset,
        })

    def post(self, request, pk):
        project = self.get_project(pk)
        ProjectDisciplineFormSet = self.get_formset_class()
        formset = ProjectDisciplineFormSet(
            request.POST,
            queryset=ProjectDiscipline.objects.filter(project=project).select_related('discipline', 'manager')
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Disciplines updated successfully.")
            return redirect(reverse("project-details", kwargs={"pk": pk}))

        return render(request, self.template_name, {
            "project": project,
            "formset": formset,
        })
        
class ProjectToggleStatusView(View):
    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        status = request.POST.get("status")

        if status in dict(Project.STATUS_CHOICES):
            project.status = status

            if status == "completed":
                # Set actual_end_date if not already set
                if not project.actual_end_date:
                    project.actual_end_date = timezone.now().date()
                project.save(update_fields=["status", "actual_end_date"])
                create_project_snapshot(project)
            else:
                project.save(update_fields=["status"])

        messages.info(request, f"Project status updated successfully to {project.get_status_display()}")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER") or "/")
    
    
import io
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame

from projects.models import Project


# ──────────────────────────────────────────────
# BRAND PALETTE
# ──────────────────────────────────────────────
NAVY       = colors.HexColor("#0D1B2A")
BLUE       = colors.HexColor("#1A73E8")
LIGHT_BLUE = colors.HexColor("#E8F0FD")
TEAL       = colors.HexColor("#0097A7")
GREEN      = colors.HexColor("#2E7D32")
AMBER      = colors.HexColor("#F57C00")
RED        = colors.HexColor("#C62828")
GREY       = colors.HexColor("#546E7A")
LIGHT_GREY = colors.HexColor("#F5F7FA")
MID_GREY   = colors.HexColor("#CFD8DC")
WHITE      = colors.white
BLACK      = colors.HexColor("#212121")

STATUS_COLORS = {
    "planning":    (AMBER,      colors.HexColor("#FFF8E1")),
    "in_progress": (BLUE,       LIGHT_BLUE),
    "on_hold":     (GREY,       colors.HexColor("#ECEFF1")),
    "completed":   (GREEN,      colors.HexColor("#E8F5E9")),
}

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm


# ──────────────────────────────────────────────
# HEADER / FOOTER CANVAS CALLBACKS
# ──────────────────────────────────────────────
def _draw_header_footer(canvas, doc, project, generated_at):
    canvas.saveState()
    w, h = A4

    # ── Top accent bar ──
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)

    # Company / report label
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(MARGIN, h - 9 * mm, "PROJECT REPORT")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - MARGIN, h - 9 * mm, project.project_number)

    # ── Thin top-blue rule under header bar ──
    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(1.5)
    canvas.line(MARGIN, h - 15 * mm, w - MARGIN, h - 15 * mm)

    # ── Footer ──
    canvas.setFillColor(LIGHT_GREY)
    canvas.rect(0, 0, w, 10 * mm, fill=1, stroke=0)

    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(MARGIN, 3.5 * mm,
                      f"Generated: {generated_at}  |  {project.name}")
    canvas.drawRightString(w - MARGIN, 3.5 * mm,
                           f"Page {doc.page}")

    canvas.restoreState()


# ──────────────────────────────────────────────
# STYLE HELPERS
# ──────────────────────────────────────────────
def _styles():
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "report_title": ps("ReportTitle",
            fontSize=22, fontName="Helvetica-Bold",
            textColor=NAVY, spaceAfter=2,
            leading=26, alignment=TA_LEFT),

        "subtitle": ps("Subtitle",
            fontSize=10, fontName="Helvetica",
            textColor=GREY, spaceAfter=6, leading=14),

        "section_heading": ps("SectionHeading",
            fontSize=11, fontName="Helvetica-Bold",
            textColor=NAVY, spaceBefore=14, spaceAfter=4,
            leading=14),

        "sub_heading": ps("SubHeading",
            fontSize=9, fontName="Helvetica-Bold",
            textColor=GREY, spaceBefore=6, spaceAfter=2),

        "body": ps("Body",
            fontSize=8.5, fontName="Helvetica",
            textColor=BLACK, leading=13, spaceAfter=2),

        "label": ps("Label",
            fontSize=7.5, fontName="Helvetica-Bold",
            textColor=GREY, leading=11),

        "value": ps("Value",
            fontSize=8.5, fontName="Helvetica",
            textColor=BLACK, leading=12),

        "badge": ps("Badge",
            fontSize=8, fontName="Helvetica-Bold",
            alignment=TA_CENTER),

        "small": ps("Small",
            fontSize=7.5, fontName="Helvetica",
            textColor=GREY, leading=10),

        "caption": ps("Caption",
            fontSize=7, fontName="Helvetica",
            textColor=GREY, alignment=TA_CENTER),
    }


def _kv_table(pairs, col_widths=None):
    """Two-column label / value table for info grids."""
    usable = PAGE_W - 2 * MARGIN
    col_widths = col_widths or [usable * 0.35, usable * 0.65]
    data = [[Paragraph(f"<b>{k}</b>", ParagraphStyle("lbl",
                fontSize=7.5, textColor=GREY, fontName="Helvetica-Bold")),
             Paragraph(str(v) if v not in (None, "") else "—",
                ParagraphStyle("val", fontSize=8.5, textColor=BLACK,
                               fontName="Helvetica"))]
            for k, v in pairs]
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_GREY]),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, MID_GREY),
        ("ROUNDEDCORNERS", [3]),
    ]))
    return t


def _section_rule():
    return HRFlowable(width="100%", thickness=0.5,
                      color=MID_GREY, spaceAfter=4, spaceBefore=4)


def _section_title(text, styles):
    return Paragraph(f"<b>{text.upper()}</b>", styles["section_heading"])


def _status_badge(status_key, display, styles):
    ink, bg = STATUS_COLORS.get(status_key, (GREY, LIGHT_GREY))
    t = Table([[Paragraph(f"<b> {display.upper()} </b>",
                           ParagraphStyle("b", fontSize=8,
                                          fontName="Helvetica-Bold",
                                          textColor=ink,
                                          alignment=TA_CENTER))]],
              colWidths=[40 * mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("ROUNDEDCORNERS", [4]),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.8, ink),
    ]))
    return t


def _progress_bar_table(pct, width=None):
    """Inline horizontal progress bar as a table."""
    usable = width or (PAGE_W - 2 * MARGIN)
    filled = max(0, min(int(usable * pct / 100), int(usable)))
    empty  = int(usable) - filled

    bar_color = GREEN if pct >= 75 else BLUE if pct >= 40 else AMBER

    inner = Table(
        [["", ""]],
        colWidths=[filled if filled > 0 else 0.1,
                   empty  if empty  > 0 else 0.1],
    )
    inner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), bar_color),
        ("BACKGROUND",    (1, 0), (1, 0), MID_GREY),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("ROUNDEDCORNERS", [3]),
    ]))
    return inner


# ──────────────────────────────────────────────
# SECTION BUILDERS
# ──────────────────────────────────────────────

def _build_cover(project, styles, story, generated_at):
    """Large title block at the top of page 1."""
    status_key = project.status
    ink, bg = STATUS_COLORS.get(status_key, (GREY, LIGHT_GREY))

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(project.name, styles["report_title"]))
    story.append(Paragraph(
        f"{project.project_number}  ·  "
        f"{project.get_project_type_display()}  ·  "
        f"Generated {generated_at}",
        styles["subtitle"],
    ))
    story.append(_status_badge(status_key,
                               project.get_status_display(), styles))
    story.append(Spacer(1, 4 * mm))
    story.append(_section_rule())


def _build_overview(project, styles, story):
    story.append(_section_title("Project Overview", styles))

    pm = project.project_manager
    pm_name = pm.get_full_name() if pm and hasattr(pm, "get_full_name") else (
        str(pm) if pm else "—"
    )
    client = project.client
    client_name = str(client) if client else "—"
    branch = project.branch
    branch_name = str(branch) if branch else "—"

    pairs = [
        ("Project Number",  project.project_number),
        ("Project Name",    project.name),
        ("Project Type",    project.get_project_type_display()),
        ("Branch",          branch_name),
        ("Client",          client_name),
        ("Project Manager", pm_name),
        ("Status",          project.get_status_display()),
    ]
    story.append(_kv_table(pairs))
    story.append(Spacer(1, 3 * mm))


def _build_schedule(project, styles, story):
    story.append(_section_title("Schedule", styles))

    today = timezone.now().date()

    def fmt(d):
        return d.strftime("%d %b %Y") if d else "—"

    # Calculate schedule variance in days
    variance_days = None
    variance_label = "—"
    if project.planned_end_date:
        end_ref = project.actual_end_date or today
        diff = (end_ref - project.planned_end_date).days
        if diff == 0:
            variance_label = "On schedule"
        elif diff > 0:
            variance_label = f"+{diff} days (delayed)"
        else:
            variance_label = f"{diff} days (early)"

    pairs = [
        ("Planned Start Date",   fmt(project.start_date)),
        ("Planned End Date",     fmt(project.planned_end_date)),
        ("Actual End Date",      fmt(project.actual_end_date)),
        ("Baseline Start",       fmt(project.baseline_start_date)),
        ("Baseline End",         fmt(project.baseline_end_date)),
        ("Schedule Variance",    variance_label),
        ("Baseline Locked",      "Yes" if project.baseline_locked else "No"),
    ]
    story.append(_kv_table(pairs))
    story.append(Spacer(1, 3 * mm))


def _build_financials(project, styles, story):
    story.append(_section_title("Financials", styles))

    budget = project.budget or 0
    baseline_budget = project.baseline_budget or 0

    # Sum confirmed expenses
    confirmed_expenses = sum(
        e.amount for e in project.expenses.filter(status="Confirmed")
    ) if hasattr(project, "expenses") else 0

    variance = budget - confirmed_expenses
    cpi = round(budget / confirmed_expenses, 2) if confirmed_expenses else "—"

    pairs = [
        ("Current Budget",       f"${budget:,.2f}"),
        ("Baseline Budget",      f"${baseline_budget:,.2f}" if baseline_budget else "—"),
        ("Confirmed Expenses",   f"${confirmed_expenses:,.2f}"),
        ("Cost Variance",        f"${variance:,.2f}" if confirmed_expenses else "—"),
        ("Cost Performance (CPI)", str(cpi)),
    ]
    story.append(_kv_table(pairs))
    story.append(Spacer(1, 3 * mm))


def _build_disciplines(project, styles, story):
    story.append(_section_title("Disciplines & Tasks", styles))

    disciplines = project.disciplines.filter(is_active=True).select_related(
        "discipline", "manager"
    ).prefetch_related("tasks__updates")

    if not disciplines.exists():
        story.append(Paragraph("No disciplines assigned to this project.", styles["body"]))
        return

    usable = PAGE_W - 2 * MARGIN

    for pd in disciplines:
        pct = pd.percent_complete

        # ── Discipline header row ──
        manager_name = str(pd.manager) if pd.manager else "Unassigned"
        disc_header_data = [[
            Paragraph(f"<b>{pd.discipline.name}</b>",
                      ParagraphStyle("dh", fontSize=9,
                                     fontName="Helvetica-Bold",
                                     textColor=NAVY)),
            Paragraph(f"Manager: {manager_name}",
                      ParagraphStyle("dm", fontSize=8,
                                     fontName="Helvetica", textColor=GREY)),
            Paragraph(f"Weight: {pd.planned_weight}%  |  "
                      f"Budget: ${pd.budget_allocated:,.0f}",
                      ParagraphStyle("db", fontSize=8,
                                     fontName="Helvetica", textColor=GREY,
                                     alignment=TA_RIGHT)),
        ]]
        disc_header = Table(disc_header_data,
                            colWidths=[usable * 0.35,
                                       usable * 0.35,
                                       usable * 0.30])
        disc_header.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_BLUE),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (0, 0),  8),
            ("RIGHTPADDING",  (-1, 0), (-1, 0), 8),
            ("LINEBELOW",     (0, 0), (-1, -1), 1, BLUE),
        ]))
        story.append(KeepTogether([disc_header]))

        # Progress bar
        bar_row = Table(
            [[_progress_bar_table(pct, usable),
              Paragraph(f"<b>{pct:.1f}%</b>",
                        ParagraphStyle("pct", fontSize=8,
                                       fontName="Helvetica-Bold",
                                       textColor=NAVY,
                                       alignment=TA_RIGHT))]],
            colWidths=[usable * 0.88, usable * 0.12],
        )
        bar_row.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        story.append(bar_row)

        # ── Tasks table ──
        tasks = pd.tasks.filter(is_active=True).select_related("assigned_to")

        if tasks.exists():
            task_header = ["Task", "Assignee", "Type",
                           "Start", "End", "Budget", "% Done"]
            task_rows = [task_header]

            for t in tasks:
                task_pct = t.percent_complete
                bar_color = (GREEN if task_pct >= 75
                             else BLUE if task_pct >= 40 else AMBER)
                assignee = str(t.assigned_to) if t.assigned_to else "—"
                task_rows.append([
                    Paragraph(t.name,
                              ParagraphStyle("tn", fontSize=7.5,
                                             fontName="Helvetica",
                                             textColor=BLACK)),
                    assignee,
                    t.get_measurement_type_display(),
                    t.planned_start.strftime("%d/%m/%y") if t.planned_start else "—",
                    t.planned_end.strftime("%d/%m/%y") if t.planned_end else "—",
                    f"${t.budgeted_cost:,.0f}",
                    f"{task_pct:.1f}%",
                ])

            col_w = [usable * w for w in [0.26, 0.16, 0.13, 0.10, 0.10, 0.12, 0.10]]
            task_table = Table(task_rows, colWidths=col_w, hAlign="LEFT",
                               repeatRows=1)
            task_table.setStyle(TableStyle([
                # Header
                ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, 0), 7),
                ("TOPPADDING",    (0, 0), (-1, 0), 4),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                # Body rows
                ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
                ("TOPPADDING",    (0, 1), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
                ("LEFTPADDING",   (0, 0), (-1, -1), 5),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
                ("ALIGN",         (3, 0), (-1, -1), "CENTER"),
                ("ALIGN",         (5, 0), (-1, -1), "RIGHT"),
                ("ALIGN",         (6, 0), (-1, -1), "CENTER"),
                ("GRID",          (0, 0), (-1, -1), 0.3, MID_GREY),
                ("LINEBELOW",     (0, 0), (-1, 0),   1,   BLUE),
            ]))
            story.append(task_table)
        else:
            story.append(Paragraph(
                "  No tasks assigned to this discipline.",
                styles["small"]
            ))

        story.append(Spacer(1, 4 * mm))


def _build_snapshot(project, styles, story):
    """Only rendered when project has a completed snapshot."""
    try:
        snap = project.snapshot
    except Exception:
        return

    story.append(_section_title("Completion Snapshot", styles))

    pairs = [
        ("Discipline Mix",            snap.discipline_mix or "—"),
        ("Actual Duration",           f"{snap.actual_duration} days"),
        ("Final SPI",                 f"{snap.final_spi:.3f}"),
        ("Final CPI",                 f"{snap.final_cpi:.3f}"),
        ("Team Size",                 str(snap.team_size)),
        ("Final Cost",                f"${snap.final_cost:,.2f}"),
        ("Budget at Completion",      f"${snap.budget_at_completion:,.2f}"),
    ]
    story.append(_kv_table(pairs))
    story.append(Spacer(1, 3 * mm))


def _build_expenses(project, styles, story):
    expenses = project.expenses.filter(is_active=True).select_related(
        "category"
    ).order_by("expense_date") if hasattr(project, "expenses") else []

    if not hasattr(project, "expenses") or not project.expenses.exists():
        return

    story.append(_section_title("Expense Log", styles))

    usable = PAGE_W - 2 * MARGIN

    status_ink = {
        "Draft": GREY, "Submitted": BLUE, "Confirmed": GREEN,
        "Rejected": RED, "Cancelled": GREY, "Reverted": AMBER,
    }

    header = ["Date", "Category", "Description", "Amount", "Status"]
    rows   = [header]
    total  = 0

    for e in expenses:
        rows.append([
            e.expense_date.strftime("%d/%m/%y") if e.expense_date else "—",
            str(e.category) if e.category else "—",
            (e.description or "—")[:55],
            f"${e.amount:,.2f}",
            e.status,
        ])
        if e.status == "Confirmed":
            total += e.amount

    # Totals row
    rows.append(["", "", Paragraph("<b>CONFIRMED TOTAL</b>",
                                    ParagraphStyle("tot", fontSize=8,
                                                   fontName="Helvetica-Bold",
                                                   textColor=NAVY)),
                 Paragraph(f"<b>${total:,.2f}</b>",
                            ParagraphStyle("totv", fontSize=8,
                                           fontName="Helvetica-Bold",
                                           textColor=GREEN)),
                 ""])

    col_w = [usable * w for w in [0.12, 0.22, 0.35, 0.15, 0.13]]
    exp_table = Table(rows, colWidths=col_w, hAlign="LEFT", repeatRows=1)
    exp_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 7),
        ("FONTNAME",      (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2), [WHITE, LIGHT_GREY]),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("ALIGN",         (3, 0), (3, -1), "RIGHT"),
        ("ALIGN",         (4, 0), (4, -1), "CENTER"),
        ("GRID",          (0, 0), (-1, -2), 0.3, MID_GREY),
        ("LINEBELOW",     (0, 0), (-1, 0),   1, BLUE),
        # Last row styling
        ("BACKGROUND",    (0, -1), (-1, -1), LIGHT_GREY),
        ("LINEABOVE",     (0, -1), (-1, -1), 1, NAVY),
        ("TOPPADDING",    (0, -1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 5),
    ]))
    story.append(exp_table)
    story.append(Spacer(1, 3 * mm))


# ──────────────────────────────────────────────
# MAIN VIEW
# ──────────────────────────────────────────────

class ProjectPDFView(View):
    def get(self, request, pk, *args, **kwargs):
        project = get_object_or_404(
            Project.objects.select_related(
                "client", "branch", "project_manager"
            ).prefetch_related(
                "disciplines__discipline",
                "disciplines__manager",
                "disciplines__tasks__assigned_to",
                "disciplines__tasks__updates",
            ),
            pk=pk,
        )

        generated_at = timezone.now().strftime("%d %b %Y, %H:%M")
        buffer = io.BytesIO()
        styles = _styles()

        # ── Doc template with header/footer callback ──
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=20 * mm,
            bottomMargin=16 * mm,
            title=f"{project.project_number} — {project.name}",
            author="Project Management System",
        )

        def on_page(canvas, doc):
            _draw_header_footer(canvas, doc, project, generated_at)

        story = []

        _build_cover(project, styles, story, generated_at)
        _build_overview(project, styles, story)
        _build_schedule(project, styles, story)
        _build_financials(project, styles, story)
        _build_disciplines(project, styles, story)

        if project.status == "completed":
            _build_snapshot(project, styles, story)

        _build_expenses(project, styles, story)

        doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

        buffer.seek(0)
        filename = f"project_{project.project_number}_report.pdf"
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )