from django.contrib import admin
from django.utils.html import format_html

from .models import Post, Booking


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "status_badge",
        "created_at",
    ]

    list_filter = [
        "published",
        "created_at",
    ]

    search_fields = [
        "title",
        "content",
    ]

    prepopulated_fields = {
        "slug": ("title",),
    }

    readonly_fields = [
        "created_at",
    ]

    fieldsets = (
        ("Article", {
            "fields": (
                "title",
                "slug",
                "content",
            )
        }),
        ("Publication", {
            "fields": (
                "published",
                "created_at",
            )
        }),
    )

    ordering = [
        "-created_at",
    ]

    actions = [
        "publish_posts",
        "unpublish_posts",
    ]

    def status_badge(self, obj):
        if obj.published:
            return format_html(
                '<span style="color: green; font-weight: bold;">Published</span>'
            )
        return format_html(
            '<span style="color: #b36b00; font-weight: bold;">Draft</span>'
        )

    status_badge.short_description = "Status"

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):
        queryset.update(published=True)

    @admin.action(description="Unpublish selected posts")
    def unpublish_posts(self, request, queryset):
        queryset.update(published=False)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "customer_name",
        "service",
        "date",
        "time_slot",
        "paid_badge",
        "email",
        "phone",
        "message_preview",
        "created_at",
    ]

    list_filter = [
        "paid",
        "service",
        "date",
        "created_at",
    ]

    search_fields = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "message",
    ]

    readonly_fields = [
        "service",
        "date",
        "time_slot",
        "first_name",
        "last_name",
        "email",
        "phone",
        "message",
        "paid",
        "created_at",
    ]

    fieldsets = (
        ("Booking status", {
            "fields": (
                "paid",
                "service",
                "date",
                "time_slot",
            )
        }),
        ("Customer", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "phone",
            )
        }),
        ("Message", {
            "fields": (
                "message",
            )
        }),
        ("Technical info", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
            )
        }),
    )

    ordering = [
        "-date",
        "-created_at",
    ]

    date_hierarchy = "date"

    def customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    customer_name.short_description = "Customer"

    def paid_badge(self, obj):
        if obj.paid:
            return format_html(
                '<span style="color: green; font-weight: bold;">Paid</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">Unpaid</span>'
        )

    paid_badge.short_description = "Payment"

    def message_preview(self, obj):
        if not obj.message:
            return "—"

        preview = obj.message[:60]

        if len(obj.message) > 60:
            preview += "..."

        return preview

    message_preview.short_description = "Message"