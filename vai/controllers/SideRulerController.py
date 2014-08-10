from ..widgets import LineBadge
from ..linting import LinterResult
from ..models.TextDocument import LineMeta
from vaitk import gui

class SideRulerController:
    def __init__(self, side_ruler):
        self._side_ruler = side_ruler
        self._edit_area_model = None
        self._document = None

    def setModels(self, document, edit_area_model):
        if self._edit_area_model:
            self._edit_area_model.documentPosChanged.disconnect(self.updateTopRow)

        if self._document:
            self._document.lineMetaInfoChanged.disconnect(self.updateBadges)
            self._document.contentChanged.disconnect(self.updateNumRows)

        self._edit_area_model = edit_area_model
        self._edit_area_model.documentPosChanged.connect(self.updateTopRow)

        self._document = document
        self._document.lineMetaInfoChanged.connect(self.updateBadges)
        self._document.contentChanged.connect(self.updateNumRows)

        self.updateTopRow()
        self.updateNumRows()
        self.updateBadges()

    def updateTopRow(self, *args):
        if self._edit_area_model:
            top_pos = self._edit_area_model.document_pos_at_top
            self._side_ruler.setTopRow(top_pos[0])

    def updateNumRows(self, *args):
        if self._document:
            self._side_ruler.setNumRows(self._document.numLines())

    def updateBadges(self, *args):
        if self._document:
            for line_num in range(1,self._document.numLines()+1):
                meta = self._document.lineMeta(line_num)
                badge = None

                lint = meta.get(LineMeta.LinterResult)
                if lint is not None:
                    if lint.level == LinterResult.Level.ERROR:
                        badge = LineBadge(marker="E",
                                          description=lint.message,
                                          fg_color=gui.VGlobalColor.yellow,
                                          bg_color=gui.VGlobalColor.red
                                )
                    elif lint.level == LinterResult.Level.WARNING:
                        badge = LineBadge(marker="W",
                                          description=lint.message,
                                          fg_color=gui.VGlobalColor.yellow,
                                          bg_color=gui.VGlobalColor.brown
                                )
                    elif lint.level == LinterResult.Level.INFO:
                        badge = LineBadge(marker="*",
                                          description=lint.message,
                                          fg_color=gui.VGlobalColor.yellow,
                                          bg_color=gui.VGlobalColor.cyan
                                        )

                change = meta.get(LineMeta.Change)
                if change == "added":
                    badge = LineBadge(marker="+", description="", fg_color=gui.VGlobalColor.white, bg_color=gui.VGlobalColor.green)
                elif change == "modified":
                    badge = LineBadge(marker=".", description="", fg_color=gui.VGlobalColor.white, bg_color=gui.VGlobalColor.magenta)


                if badge is None:
                    self._side_ruler.removeBadge(line_num)
                else:
                    self._side_ruler.addBadge(line_num, badge)

