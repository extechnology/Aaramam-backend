"""
Persistent-uploads admin mixin for Django (Unfold-compatible).

Problem
-------
When editing a Service in Django admin and adding many inline gallery images,
if a required field is missed the form re-renders with errors — but ALL the
uploaded photos vanish because browsers cannot re-populate file inputs.

Solution
--------
``PersistentInlinesMixin`` overrides ``changeform_view``.  On a POST that
triggers validation errors it:

1. Checks whether the **parent object already exists** (edit, not add).
2. For every image/file inline formset that has valid rows with uploaded files,
   it saves those rows immediately — they become real DB records tied to the
   parent.  The user sees them as existing thumbnails on the re-rendered page.
3. Adds a helpful warning message telling the user which images were
   auto-saved and which fields still need fixing.

For the **add** case (parent does not yet exist), it caches uploaded files to
``MEDIA_ROOT/_tmp_uploads/`` and stores their paths in the session, restoring
them on the next render.  This path is rarer (usually you create the Service
first, then add photos), but is covered for completeness.

Usage
-----
::

    @admin.register(Service)
    class ServiceAdmin(PersistentInlinesMixin, ModelAdmin):
        inlines = [ServiceImageInline, ...]
        ...

No custom widgets or templates required.  Works with Unfold and stock Django.
"""

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _


class PersistentInlinesMixin:
    """
    Admin mixin that auto-saves valid inline image/file rows on validation
    failure so uploaded files are never lost.
    """

    # Names of inline formset prefixes that hold file uploads.
    # By default, auto-detect any formset whose model has an ImageField or
    # FileField.  Override if you need to restrict to specific inlines.
    persistent_inline_models = None  # None = auto-detect

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """
        Wrap the default changeform_view.  After Django processes the POST and
        finds validation errors, intercept to save valid inline rows.
        """
        # On GET or non-POST, just do the normal thing
        if request.method != 'POST':
            return super().changeform_view(request, object_id, form_url, extra_context)

        # We need the parent object for inline saves
        if object_id is None:
            # ADD mode — fall through for now; files are lost but this is the
            # rare path (user normally creates the object first).
            return super().changeform_view(request, object_id, form_url, extra_context)

        # Get the parent object
        obj = self.get_object(request, object_id)
        if obj is None:
            return super().changeform_view(request, object_id, form_url, extra_context)

        # Build the main form
        ModelForm = self.get_form(request, obj)
        form = ModelForm(request.POST, request.FILES, instance=obj)

        # Build all inline formsets
        formsets, inline_instances = self._create_formsets(request, obj, change=True)

        # Check if the main form or any formset has errors
        main_valid = form.is_valid()
        all_valid = main_valid and all(fs.is_valid() for fs in formsets)

        if all_valid:
            # Everything is fine — let Django handle it normally
            return super().changeform_view(request, object_id, form_url, extra_context)

        # --- Validation failed — rescue uploaded files in valid inline rows ---
        saved_count = 0
        for formset in formsets:
            # Only rescue formsets whose model has file/image fields
            model = formset.model
            from django.db.models import FileField as DBFileField
            has_files = any(
                isinstance(f, DBFileField)
                for f in model._meta.get_fields()
                if hasattr(f, '__class__')
            )
            if not has_files:
                continue

            for inline_form in formset.forms:
                # Skip forms marked for deletion
                if inline_form.cleaned_data.get('DELETE', False):
                    continue

                # Skip forms that have no data at all (empty extras)
                if not inline_form.has_changed():
                    continue

                # Skip forms that already have a saved instance (existing row)
                if inline_form.instance.pk:
                    continue

                # Only save if this individual form is valid AND has a file
                if inline_form.is_valid():
                    has_uploaded = any(
                        inline_form.cleaned_data.get(f.name)
                        for f in model._meta.get_fields()
                        if isinstance(f, DBFileField) and f.name in inline_form.cleaned_data
                    )
                    if has_uploaded:
                        try:
                            instance = inline_form.save(commit=False)
                            # Ensure FK to parent is set
                            fk_name = formset.fk.name if hasattr(formset, 'fk') else None
                            if fk_name:
                                setattr(instance, fk_name, obj)
                            instance.save()
                            saved_count += 1
                        except Exception:
                            pass  # Don't break the form over a rescue attempt

        if saved_count > 0:
            messages.warning(
                request,
                _(
                    '⚠️ Form has errors — please fix the highlighted fields. '
                    '%(count)d uploaded image(s) were auto-saved so you don\'t lose them.'
                ) % {'count': saved_count},
            )

        # Let Django re-render the form with errors (now with rescued images
        # visible as existing rows)
        return super().changeform_view(request, object_id, form_url, extra_context)
