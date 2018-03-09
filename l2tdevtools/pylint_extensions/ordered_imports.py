from __future__ import unicode_literals
import astroid

from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker


class OrderedImports(BaseChecker):
  __implements__ = IAstroidChecker

  name = 'ordered-imports-checker'

  UNORDERED_IMPORT_FROM = 'unordered-import-from'

  DIR_HIGHER = 'higher'
  DIR_LOWER = 'lower'

  # Messages
  msgs = {
    'C6001': '%s in %s is in wrong position. Move it %s. ' + UNORDERED_IMPORT_FROM + 'See the style guide'
  }

  options = ()

  priority = -1

  def visit_importfrom(self, node):
    """Callback for investigation.

    Args:
      node (astroid.node_classes.ImportFrom): node being visited.
    """
    names = [name for name, _alias in node.names]

    # Desired ordering
    sorted_names = sorted(names)

    for actual_index, name in enumerate(names):
      correct_index = sorted_names.index(name)

      if correct_index != actual_index:
        direction = self.DIR_LOWER
        if correct_index < actual_index:
          direction = self.DIR_HIGHER
        args = (name, node.as_string(), direction)
        self.add_message(self.UNORDERED_IMPORT_FROM, node=node, args=args)



def register(linter):
  linter.register_checker(OrderedImports(linter))