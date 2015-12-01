"""
AinneveList module.

The main feature of this module is the AinneveList building class that
provides formatting support for lists in Ainneve. It supports easy
creation of one, two, or three column lists.

Data for an AinneveList can be a simple list of strings, a dict of
label: value pairs, or a list of dicts containing keys that describe
the items' label, value, and additional keys that can override list-level
arguments passed into the constructor on an individual item basis. See
the class docstring for more on which arguments can be overridden on a
per-item basis.

List items do not wrap. Items that are longer than their allotted space
are truncated.

AinneveList supports custom list item sorting by including additional sort
keys on list items and using the `orderby` and `fill_dir` arguments.
Combined, these control the distribution of items across columns.

List items can be colored using the `lcolor` and `vcolor` arguments or
item keys. List items may also be colored by using ANSI color codes within
the item text.

For even greater control, a custom `layout` property may be set. Layouts
consist of a number of defined columns and offset spaces on a `width` / 6
grid. A layout is a list of strings beginning with either "column" or
"offset", then a dash, then the number of grid spaces to allocate. Thus
the default two-column layout is

    ['column-3', 'column-3']

And a custom two column split layout could be:

    ['column-3', 'offset-1', 'column-2']

This would produce two columns of different widths, separated by a single
empty grid column.

All six grid spaces do not need to be accounted for.

    ['offset-1', 'column-4']

This provides a single column indented from both the left and right sides
by one grid unit.

If `layout` is specified, it overrides any value entered for `columns`.
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

    All constructor arguments are optional, but the list will
    not render until either `columns` or `layout` is set, as well
    as `data`.

    Args:
        data (list, dict): data to list, either a list of items,
            a dict of label:item pairs, or a dict containing keys
            'lbl', 'val', and additional data used for sorting
        columns (int): number of columns for list, typically 1-3
        fill_dir (str): one of 'h' for horizontal or 'v' for vertical
        orderby (str, callable): key or function to order dict-based lists
        width (int): total width of the screen in characters; default 79
        lsep (str): separator for label: item pairs. overrideable per-item
        lcolor (str): ansi color code for labels. overrideable per-item
        vcolor (str): ansi color code for values. overrideable per-item
        vwidth (int): columns to allocate for value. overrideable per-item
            label gets remaining space. setting to zero hides 'lbl' giving
            'val' full column width.
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
        self.re_colors = re.compile(r'\|\[?(?:\d{3}|[RrGgBbYyCcMmWwX])(?:\|\[(?:\d{3}|[RrGgBbYyCcMmWwX]))?$')
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
            if not isinstance(data[0], dict):
                self._data = [{'val': str(v), 'vwidth': 0}
                              for v in data]
            else:
                self._data = data
        else:
            raise AnvListException("`data` must be a list, dict, or list of dicts.")
        self._parse_layout()
        self._refresh_list()

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
            self._parse_layout()
            self._refresh_list()
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
            self._refresh_list()
        else:
            raise AnvListException('Invalid fill_dir specified.')

    @property
    def width(self):
        """Total width of the list. Defaults to 79 characters."""
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._parse_layout()
        self._refresh_list()

    @property
    def lsep(self):
        """Label separator"""
        return self._lsep

    @lsep.setter
    def lsep(self, sep):
        self._lsep = sep
        self._refresh_list()

    @property
    def lcolor(self):
        """Label color.

        Note:
            Accepts new |-style ANSI color codes only."""
        return self._lcolor

    @lcolor.setter
    def lcolor(self, color):
        if re.match(self.re_colors, color):
            self._lcolor = color
            self._refresh_list()

    @property
    def vcolor(self):
        """Value color.

        Note:
            Accepts new |-style ANSI color codes only."""
        return self._vcolor

    @vcolor.setter
    def vcolor(self, color):
        if re.match(self.re_colors, color):
            self._vcolor = color
            self._refresh_list()

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
        self._refresh_list()

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
        self._refresh_list()

    @property
    def has_border(self):
        """True if list and column borders should be drawn."""
        return self._has_border

    @has_border.setter
    def has_border(self, value):
        self._has_border = bool(value)
        self._refresh_list()

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
        self._parse_layout()
        self._refresh_list()

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

    def _parse_layout(self):
        """Builds the internal representation of the layout."""
        # calculate an even 6 column split
        num_cols = len(self.layout)
        adj_width = (self.width - num_cols - 1
                     if self.has_border else self.width)
        splitsize = 1.0 / 6 * adj_width
        grid_widths = [int(round((i+1)*splitsize)) - int(round(i*splitsize))
                       for i in xrange(6)]

        # then combine columns as described in the layout
        self.col_data = []
        cur = 0
        for col in self.layout:
            type, width = col.split('-')
            self.col_data.append({
                'type': type,
                'width': sum(grid_widths[cur:cur+int(width)])
            })
            cur += int(width)

        self.col_data.append({})
        border_char = {'column': _CHAR_H, 'offset': _CHAR_S}
        col_borders = [border_char[cdata['type']] * cdata['width']
                       for cdata in self.col_data[:-1]]

        self._border = (
            _CHAR_J +
            _CHAR_J.join(col_borders) +
            _CHAR_J
        )

    def _refresh_list(self):
        """Renders the list data into the layout and stores in lines."""
        self.lines = []
        if self.data is None:
            return

        # handle orderby
        if self.orderby:
            items = sorted(self.data, key=self.orderby)
        else:
            items = self.data

        # pad the items collection if needed for even columns
        columns = sum(1 for x in self.col_data[:-1] if x['type'] == 'column')
        if len(items) % columns > 0:
            items += [{'val': '', 'vwidth': 0}
                      for _ in xrange(columns - (len(items) % columns))]

        # break the items into rows using fill_dir
        if self.fill_dir == 'h':
            lines = [items[i:i+columns]
                     for i in xrange(0, len(items), columns)]
        elif self.fill_dir == 'v':
            split = len(items) // columns
            lines = [[items[i+j*split] for j in xrange(columns)]
                     for i in xrange(split)]
        else:
            assert False

        if len(items) > 0 and isinstance(items[0], dict):
            for line in lines:
                cols = []
                i = 0
                for item in line:
                    vwidth = item.get('vwidth', self.vwidth)

                    if vwidth <= 0:
                        vwidth = self.col_data[i]['width'] - 2 * self.padding

                    lwidth = (self.col_data[i]['width'] - 4 * self.padding -
                              len(item.get('lsep', self.lsep)) - vwidth)

                    vwidth += self._ansi_count(item['val'])
                    lwidth += self._ansi_count(item.get('lbl', ''))

                    # set widths to zero if they are negative
                    vwidth = 0 if vwidth < 0 else vwidth
                    lwidth = 0 if lwidth < 0 else lwidth

                    vcolor = item.get('vcolor', self.vcolor)
                    lcolor = item.get('lcolor', self.lcolor)

                    opts = dict(
                        lbl=str(item.get('lbl', '')),
                        lcolor=lcolor,
                        lclear='|n' if lcolor else '',
                        lwidth=lwidth,
                        lsep=item.get('lsep', self.lsep),
                        val=str(item['val']),
                        vcolor=vcolor,
                        vclear='|n' if vcolor else '',
                        vwidth=vwidth
                    )

                    if 'lbl' in item:
                        cols.append(
                            ("{pad}{lcolor}"
                             "{lbl:<{lwidth}.{lwidth}s}"
                             "{lclear}{pad}{lsep}{pad}{vcolor}"
                             "{val:>{vwidth}.{vwidth}s}"
                             "{vclear}{pad}"
                             ).format(
                                pad=' ' * self.padding,
                                **opts)
                        )
                    else:
                        cols.append(
                            ("{pad}{vcolor}"
                             "{val:<{vwidth}.{vwidth}s}"
                             "{vclear}{pad}"
                             ).format(
                                pad=' ' * self.padding,
                                **opts)
                        )
                    # check the next column to the right;
                    # if it is of type "offset", we include its spaces
                    i += 1
                    if self.col_data[i].get('type', '') == 'offset':
                        cols.append(' ' * self.col_data[i]['width'])
                        i += 1

                colsep = _CHAR_V if self.has_border else ''
                self.lines.append(
                    colsep +
                    colsep.join(cols) +
                    colsep
                )

        if self.has_border:
            self.lines.insert(0, self._border)
            self.lines.append(self._border)

    def _ansi_count(self, string):
        """Returns the number of ansi color characters."""
        from evennia.utils.ansi import strip_ansi
        string = str(string)
        return len(string) - len(strip_ansi(string))

    def __unicode__(self):
        """Display the output list."""
        return u'\n'.join(self.lines)

    def __str__(self):
        """Display the output list."""
        return '\n'.join(self.lines)
