import sys
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint

class WindowAnimator:
    """
    Sleek, GPU-accelerated window transitions for PySide6 / Qt.
    Fades windowOpacity and adds subtle directional micro-slide.
    Accelerated directly via Windows Desktop Window Manager (DWM).
    """

    @staticmethod
    def animate_open(widget, target_opacity=1.0, duration=180, slide_distance=12):
        if hasattr(widget, '_anim_group') and widget._anim_group:
            try:
                widget._anim_group.stop()
            except Exception:
                pass
            widget._anim_group = None

        widget._is_animating_close = False

        # Get intended baseline position
        target_pos = getattr(widget, '_normal_pos', None)
        if target_pos is None:
            target_pos = widget.pos()
            widget._normal_pos = target_pos

        start_pos = QPoint(target_pos.x(), target_pos.y() + slide_distance)
        widget.setWindowOpacity(0.0)
        widget.move(start_pos)
        widget.show()
        widget.raise_()
        widget.activateWindow()

        anim_group = QParallelAnimationGroup(widget)

        fade_anim = QPropertyAnimation(widget, b"windowOpacity")
        fade_anim.setDuration(duration)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(float(target_opacity))
        fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        anim_group.addAnimation(fade_anim)

        pos_anim = QPropertyAnimation(widget, b"pos")
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(target_pos)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        anim_group.addAnimation(pos_anim)

        def _on_opened():
            widget._anim_group = None
            widget.setWindowOpacity(float(target_opacity))
            widget.move(target_pos)

        anim_group.finished.connect(_on_opened)
        widget._anim_group = anim_group
        anim_group.start()

    @staticmethod
    def animate_close(widget, on_finished=None, duration=130, slide_distance=8):
        if getattr(widget, '_is_animating_close', False):
            return

        widget._is_animating_close = True

        if hasattr(widget, '_anim_group') and widget._anim_group:
            try:
                widget._anim_group.stop()
            except Exception:
                pass
            widget._anim_group = None

        normal_pos = getattr(widget, '_normal_pos', widget.pos())
        current_pos = widget.pos()
        end_pos = QPoint(normal_pos.x(), normal_pos.y() + slide_distance)
        current_opacity = widget.windowOpacity()
        if current_opacity < 0.05:
            current_opacity = 1.0

        anim_group = QParallelAnimationGroup(widget)

        fade_anim = QPropertyAnimation(widget, b"windowOpacity")
        fade_anim.setDuration(duration)
        fade_anim.setStartValue(current_opacity)
        fade_anim.setEndValue(0.0)
        fade_anim.setEasingCurve(QEasingCurve.InCubic)
        anim_group.addAnimation(fade_anim)

        pos_anim = QPropertyAnimation(widget, b"pos")
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(current_pos)
        pos_anim.setEndValue(end_pos)
        pos_anim.setEasingCurve(QEasingCurve.InCubic)
        anim_group.addAnimation(pos_anim)

        def _on_closed():
            widget._is_animating_close = False
            widget._anim_group = None
            widget.hide()
            widget.move(normal_pos)
            widget.setWindowOpacity(1.0)
            if on_finished:
                on_finished()

        anim_group.finished.connect(_on_closed)
        widget._anim_group = anim_group
        anim_group.start()
