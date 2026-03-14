from django.contrib import admin
from .models import ConstructionReport


@admin.register(ConstructionReport)
class ConstructionReportAdmin(admin.ModelAdmin):
    list_display  = ["title", "severity", "status", "address_name", "like_count", "view_count", "created_at"]
    list_filter   = ["status", "severity"]
    search_fields = ["title", "description", "address_name"]
    readonly_fields = ["id", "created_at", "updated_at", "view_count", "like_count"]
    ordering      = ["-created_at"]

    actions = ["approve_reports", "reject_reports", "resolve_reports"]

    @admin.action(description="Tanlangan hisobotlarni APPROVE qilish")
    def approve_reports(self, request, queryset):
        queryset.update(status=ConstructionReport.APPROVED)

    @admin.action(description="Tanlangan hisobotlarni REJECT qilish")
    def reject_reports(self, request, queryset):
        queryset.update(status=ConstructionReport.REJECTED)

    @admin.action(description="Tanlangan hisobotlarni RESOLVED qilish")
    def resolve_reports(self, request, queryset):
        queryset.update(status=ConstructionReport.RESOLVED)
