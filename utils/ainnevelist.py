"""
AinneveList module.

The main feature of this module is the AinneveList building class that
provides formatting support for lists in Ainneve. It supports easy
creation of one, two, or three column lists.

List items can consist of simple string values, or of a dict describing
label-value pairs. AinneveList also supports custom list item sorting
by formatting list items with additional sort keys and using the
`orderby` argument and `fill_dir` provides great flexibility in the
distribution of items across columns.

"""
import re

_CHAR_J = '+'
_CHAR_H = '-'
_CHAR_V = '||'
_CHAR_S = ' '
_LAYOUTS = {'1col': ['column-6'],
            '2col': ['column-3', 'column-3'],
            '3col': ['column-2', 'column-2', 'column-2']}


class AnvListException(Exception):
    """Base exception class for AinneveList operations."""
    def __init__(self, msg):
        self.msg = msg


class AinneveList(object):
    """Provides standardized list formatting for Ainneve.

    Supports standard one, two, or three-column layouts via the
    columns argument, or up to six columns and custom options

    Args:
        data (list, dict): data to list, either a list of items,
            a dict of label:item pairs, or a dict containing keys
            'lbl', 'val', and additional data used for sorting
        columns (int): number of columns for list, typically 1-3
        fill_dir (str): one of 'h' for horizontal or 'v' for vertical
        orderby (str, callable): key or function to order dict-based lists
        width (int): total width of the screen in characters; default 79
        lsep (str): separator for label: item pairs
        lcolor (str): ansi color code for labels
        vcolor (str): ansi color code for values
        vwidth (str): columns to allocate for value (label takes remaining)
        padding (int): number of spaces to pad list cells
        has_border (bool): draw borders around columns if True
        layout (list[str]): optional layout dict
    """

    def __init__(self,
                 data=None,
                 columns=None,
                 fill_dir='h',
                 orderby=None,
                 width=79,
                 lsep=':',
                 lcolor='',
                 vcolor='',
                 vwidth=3,
                 padding=1,
                 has_border=True,
                 layout=None):
        self._data = self._layout = self.lines = []
        self.template = {}
        self._columns = columns
        self._fill_dir = fill_dir
        self._width = width
        self._lsep = lsep
        self._lcolor = lcolor
        self._vcolor = vcolor
        self._vwidth = vwidth
        self._padding = padding
        self._has_border = has_border

        if orderby is None or callable(orderby):
            self.orderby = orderby
        else:
            self.orderby = lambda x: x[orderby]

        self.layout = layout
        self.data = data

    @property
    def data(self):
        """Property representing the list data to be displayed.

        Note:
            Setter parses dicts into internal representation of list
            of dicts.
        """
        return self._data

    @data.setter
    def data(self, data):
        if isinstance(data, dict) and len(data) > 0:
            self._data = [{'lbl': l, 'val': str(v)}
                          for l, v in data.iteritems()]
        elif data is None:
            self._data = data
        elif isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                for d in data:
                    d['val'] = str(d['val'])
            self._data = data
        else:
            raise AnvListException("`data` must be a list, dict, or list of dicts.")
        self._build_template()
        self._apply_template()

    @property
    def columns(self):
        """Number of columns in basic layout.

        Note:
            If set to None, a `layout` must be specified instead.
            If `layout` is set, this is ignored.
        """
        return self._columns

    @columns.setter
    def columns(self, value):
        if 0 < value <= 3:
            self._columns = value
            self._build_template()
            self._apply_template()
        elif value is None and self.layout is not None:
            self._columns = value
        else:
            raise AnvListException("Invalid value for `columns`.")

    @property
    def fill_dir(self):
        """Direction to fill list contents.

        Values:
            'h' - fill columns horizontally
            'v' - fill columns vertically
        """
        return self._fill_dir

    @fill_dir.setter
    def fill_dir(self, dir):
        if dir in ('h', 'v'):
            self._fill_dir = dir
            self._apply_template()
        else:
            raise AnvListException('Invalid fill_dir specified.')

    @property
    def width(self):
        """Total width of the list. Defaults to 79 characters."""
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._build_template()
        self._apply_template()

    @property
    def lsep(self):
        """Label separator"""
        return self._lsep

    @lsep.setter
    def lsep(self, sep):
        self._lsep = sep
        self._build_template()
        self._apply_template()

    @property
    def lcolor(self):
        """Label color.

        Note:
            Accepts new |-style ANSI color codes only."""
        return self._lcolor

    @lcolor.setter
    def lcolor(self, color):
        if re.match(r'\|', color):
            self._lcolor = color
            self._build_template()
            self._apply_template()

    @property
    def vcolor(self):
        """Value color.

        Note:
            Accepts new |-style ANSI color codes only."""
        return self._vcolor

    @vcolor.setter
    def vcolor(self, color):
        if re.match(r'\|', color):
            self._vcolor = color
            self._build_template()
            self._apply_template()

    @property
    def vwidth(self):
        """Value width.

        Note:
            Label gets all remaining space after padding, separator, etc.
        """
        return self._vwidth

    @vwidth.setter
    def vwidth(self, value):
        self._vwidth = value
        self._build_template()
        self._apply_template()

    @property
    def padding(self):
        """Horizontal padding for all list items.

        Note:
            label/value separators are also padded
        """
        return self._padding

    @padding.setter
    def padding(self, value):
        self._padding = value
        self._build_template()
        self._apply_template()

    @property
    def has_border(self):
        """True if list and column borders should be drawn."""
        return self._has_border

    @has_border.setter
    def has_border(self, value):
        self._has_border = bool(value)

    @property
    def layout(self):
        """Property representing the list's column layout.

        Note:
            Setter validates incoming layout and updates list state.
        """
        return self._layout

    @layout.setter
    def layout(self, value):
        self._layout = self._validate_layout(value)
        self._build_template()
        self._apply_template()

    def _validate_layout(self, layout):
        """Validates any passed-in layout or assigns a builtin layout."""
        if layout is not None:
            if isinstance(layout, list):
                if (all(re.match(r'(?:column|offset)-[1-6]$', i)
                        for i in layout)
                        and sum(int(l.split('-')[1]) for l in layout) <= 6
                        and 'offset' not in layout[-1]):
                    return layout
            raise AnvListException('Invalid layout specified.')
        elif self.columns is not None:
            return _LAYOUTS['{}col'.format(self.columns)]
        else:
            raise AnvListException('`layout` and `columns` cannot both be None.')

    def _build_template(self):
        """Builds the internal representation of the layout."""
        self.num_cols = len(self.layout)
        adj_width = (self.width - self.num_cols - 1 if self.has_border
                                                    else self.width)
        self.col_data = []
        self.template = {}
        # calculate an even 6 column split
        splitsize = 1.0 / 6 * adj_width
        col_widths = []
        for i in xrange(6):
            col_widths.append(
                int(round((i+1)*splitsize)) - int(round(i*splitsize))
            )

        # then combine columns as described in the layout
        cur = 0
        for col in self.layout:
            type, width = col.split('-')
            self.col_data.append({
                'type': type,
                'width': sum(col_widths[cur:cur+int(width)])
            })
            cur += int(width)

        if self.has_border:
            border_char = {'column': _CHAR_H, 'offset': _CHAR_S}
            col_borders = [border_char[cdata['type']] * cdata['width']
                           for cdata in self.col_data]

            self.template['border'] = (
                _CHAR_J +
                _CHAR_J.join(col_borders) +
                _CHAR_J
            )
        else:
            self.template['border'] = ''

        cols = []
        ix = 0
        if self.data is not None and len(self.data) > 0:
            if isinstance(self.data[0], dict):
                for cdata in self.col_data:
                    if cdata['type'] == 'column':
                        lwidth = (cdata['width'] - 4*self.padding
                                  - self.vwidth - len(self.lsep))
                        cols.append(
                            ("{pad}{lcolor}{{lbl{col}:<{{lwidth}}.{{lwidth}}s}}{lclr}{pad}{sep}"
                             "{pad}{vcolor}{{val{col}:>{{vwidth}}.{{vwidth}}s}}{vclr}{pad}"
                             ).format(col=ix,
                                      pad=' ' * self.padding,
                                      sep=self.lsep,
                                      lcolor=self.lcolor,
                                      vcolor=self.vcolor,
                                      lclr='|n' if self.lcolor else '',
                                      vclr='|n' if self.vcolor else '',
                                      ))
                        ix += 1
                    elif cdata['type'] == 'offset':
                        cols.append(_CHAR_S * cdata['width'])
                    else:
                        raise AnvListException('Invalid format specified.')
            else:
                for cdata in self.col_data:
                    if cdata['type'] == 'column':
                        cols.append(
                            "{pad}{vcolor}{{val{col}:<{{width}}.{{width}}s}}{vclr}{pad}".format(
                                col=ix,
                                pad=' ' * self.padding,
                                vcolor=self.vcolor,
                                width=cdata['width'] - 2*self.padding,
                                vclr='|n' if self.vcolor else '',
                            ))
                        ix += 1
                    elif cdata['type'] == 'offset':
                        cols.append(_CHAR_S * cdata['width'])
                    else:
                        raise AnvListException('Invalid format specified.')

        colsep = _CHAR_V if self.has_border else ''
        self.template['body'] = (
            colsep +
            colsep.join(cols) +
            colsep
        )

    def _apply_template(self):
        """Renders the list data into the template."""
        if self.data is None:
            self.lines = []
            return

        if self.orderby:
            items = sorted(self.data, key=self.orderby)
        else:
            items = self.data

        columns = sum(1 for x in self.col_data if x['type'] == 'column')
        if len(items) % columns > 0:
            if isinstance(items[0], dict):
                items += [{'lbl': ' ', 'val': ' '}
                          for _ in xrange(columns - (len(items) % columns))]
            else:
                items += [None for _ in xrange(len(items) % columns)]

        if self.fill_dir == 'h':
            lines = [items[i:i+columns]
                     for i in xrange(0, len(items), columns)]

        elif self.fill_dir == 'v':
            split = len(items) // columns
            lines = [[items[i+j*split] for j in xrange(columns)]
                     for i in xrange(split)]
        else:
            assert False

        self.lines = []

        if len(items) > 0 and isinstance(items[0], dict):
            for line in lines:
                opts = {'lbl{}'.format(i): line[i]['lbl']
                        for i in xrange(len(line))}
                opts.update({'val{}'.format(i): line[i]['val']
                             for i in xrange(len(line))})
                self.lines.append(
                    self.template['body'].format(**opts)
                )
        else:
            for line in lines:
                opts = {'val{}'.format(i): line[i]
                        for i in xrange(len(line))}
                self.lines.append(
                    self.template['body'].format(**opts)
                )
        if self.has_border:
            self.lines.insert(0, self.template['border'])
            self.lines.append(self.template['border'])

    def __unicode__(self):
        """Display the output list."""
        return u'\n'.join(self.lines)

    def __str__(self):
        """Display the output list."""
        return '\n'.join(self.lines)
