"""Shared server-rendered form recovery helpers."""


def focus_first_error(form) -> None:
    """Mark the first visible invalid field for native focus after rerender."""
    for field_name in form.errors:
        field = form.fields.get(field_name)
        if field is not None and not field.widget.is_hidden:
            field.widget.attrs.setdefault("autofocus", True)
            return
